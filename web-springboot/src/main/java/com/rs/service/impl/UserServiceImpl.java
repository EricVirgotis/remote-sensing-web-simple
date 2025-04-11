package com.rs.service.impl;

import cn.hutool.core.util.IdUtil;
import cn.hutool.crypto.digest.BCrypt;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rs.common.Constants;
import com.rs.dto.UserInfoDTO;
import com.rs.dto.UserLoginDTO;
import com.rs.dto.UserRegisterDTO;
import com.rs.entity.User;
import com.rs.exception.BusinessException;
import com.rs.mapper.UserMapper;
import com.rs.service.UserService;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.RequestAttributes;

import java.time.Duration;
import java.time.LocalDateTime;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * 用户服务实现类
 */
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long register(UserRegisterDTO registerDTO) {
        // 检查用户名是否已存在
        LambdaQueryWrapper<User> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(User::getUsername, registerDTO.getUsername());
        if (this.count(queryWrapper) > 0) {
            throw new BusinessException("用户名已存在");
        }
        
        // 检查两次密码是否一致
        if (!registerDTO.getPassword().equals(registerDTO.getConfirmPassword())) {
            throw new BusinessException("两次密码不一致");
        }
        
        // 创建用户对象
        User user = new User();
        user.setUsername(registerDTO.getUsername());
        // 密码加密存储
        user.setPassword(BCrypt.hashpw(registerDTO.getPassword()));
        user.setRealName(registerDTO.getRealName());
        user.setEmail(registerDTO.getEmail());
        user.setPhone(registerDTO.getPhone());
        user.setRole(Constants.UserRole.USER);
        user.setStatus(Constants.UserStatus.ENABLED);
        user.setCreateTime(LocalDateTime.now());
        user.setUpdateTime(LocalDateTime.now());
        
        // 保存用户
        this.save(user);
        
        return user.getId();
    }

    @Override
    public String login(UserLoginDTO loginDTO) {
        // 根据用户名查询用户
        LambdaQueryWrapper<User> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(User::getUsername, loginDTO.getUsername());
        User user = this.getOne(queryWrapper);
        
        // 用户不存在或密码错误
        if (user == null || !BCrypt.checkpw(loginDTO.getPassword(), user.getPassword())) {
            throw new BusinessException("用户名或密码错误");
        }
        
        // 检查用户状态
        if (user.getStatus() == Constants.UserStatus.DISABLED) {
            throw new BusinessException("账号已被禁用");
        }
        
        // 生成token（实际项目中应使用JWT等方式）
        String token = IdUtil.fastSimpleUUID();
        
        // 将token与用户ID关联存储到Redis，设置过期时间为7天
        redisTemplate.opsForValue().set(
            Constants.REDIS_TOKEN_PREFIX + token,
            user.getId(),
            Duration.ofDays(7)
        );
        
        return token;
    }

    @Override
    public UserInfoDTO getUserInfo(Long userId) {
        // 查询用户
        User user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        
        // 转换为DTO
        UserInfoDTO userInfoDTO = new UserInfoDTO();
        BeanUtils.copyProperties(user, userInfoDTO);
        
        return userInfoDTO;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateUserInfo(Long userId, UserInfoDTO userInfoDTO) {
        // 查询用户
        User user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        
        // 更新用户信息
        user.setRealName(userInfoDTO.getRealName());
        user.setEmail(userInfoDTO.getEmail());
        user.setPhone(userInfoDTO.getPhone());
        user.setAvatarUrl(userInfoDTO.getAvatar());
        user.setUpdateTime(LocalDateTime.now());
        
        return this.updateById(user);
    }

    @Override
    public Page<User> getUserPage(Page<User> page, String username, Integer status) {
        LambdaQueryWrapper<User> queryWrapper = new LambdaQueryWrapper<>();
        // 添加查询条件
        queryWrapper.like(username != null, User::getUsername, username);
        queryWrapper.eq(status != null, User::getStatus, status);
        // 按创建时间降序排序
        queryWrapper.orderByDesc(User::getCreateTime);
        
        return this.page(page, queryWrapper);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateUserStatus(Long userId, Integer status) {
        // 查询用户
        User user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        
        // 不能修改管理员状态
        if (Constants.UserRole.ADMIN.equals(user.getRole())) {
            throw new BusinessException("不能修改管理员状态");
        }
        
        // 更新状态
        user.setStatus(status);
        user.setUpdateTime(LocalDateTime.now());
        
        return this.updateById(user);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean resetPassword(Long userId, String newPassword) {
        // 查询用户
        User user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        
        // 更新密码
        user.setPassword(BCrypt.hashpw(newPassword));
        user.setUpdateTime(LocalDateTime.now());
        
        return this.updateById(user);
    }

    @Override
    public boolean logout() {
        // 从请求上下文中获取当前用户token
        String token = (String) RequestContextHolder.getRequestAttributes()
                .getAttribute(Constants.TOKEN_HEADER, RequestAttributes.SCOPE_REQUEST);
                
        if (token != null) {
            // 清除Redis中的token缓存
            redisTemplate.delete(Constants.REDIS_TOKEN_PREFIX + token);
            
            // 清除请求上下文中的token
            RequestContextHolder.getRequestAttributes()
                .removeAttribute(Constants.TOKEN_HEADER, RequestAttributes.SCOPE_REQUEST);
        }
        
        return true;
    }
}