package com.rs.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.rs.common.Result;
import com.rs.dto.UserInfoDTO;
import com.rs.dto.UserLoginDTO;
import com.rs.dto.UserRegisterDTO;
import com.rs.entity.User;
import com.rs.service.UserService;
import com.rs.utils.TokenUtils;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 用户控制器
 */
@Tag(name = "用户管理", description = "用户相关接口")
@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private UserService userService;
    
    @Autowired
    private TokenUtils tokenUtils;

    @Operation(summary = "用户注册")
    @PostMapping("/register")
    public Result<Long> register(@RequestBody UserRegisterDTO registerDTO) {
        return Result.success(userService.register(registerDTO));
    }

    @Operation(summary = "用户登录")
    @PostMapping("/login")
    public Result<String> login(@RequestBody UserLoginDTO loginDTO) {
        return Result.success(userService.login(loginDTO));
    }

    @Operation(summary = "获取用户信息")
    @GetMapping("/{userId}")
    public Result<UserInfoDTO> getUserInfo(
            @Parameter(description = "用户ID") @PathVariable Long userId) {
        return Result.success(userService.getUserInfo(userId));
    }

    @Operation(summary = "更新用户信息")
    @PutMapping("/{userId}")
    public Result<Boolean> updateUserInfo(
            @Parameter(description = "用户ID") @PathVariable Long userId,
            @RequestBody UserInfoDTO userInfoDTO) {
        return Result.success(userService.updateUserInfo(userId, userInfoDTO));
    }

    @Operation(summary = "分页查询用户列表（管理员）")
    @GetMapping("/page")
    public Result<Page<User>> getUserPage(
            @Parameter(description = "页码") @RequestParam(defaultValue = "1") Integer current,
            @Parameter(description = "每页条数") @RequestParam(defaultValue = "10") Integer size,
            @Parameter(description = "用户名") @RequestParam(required = false) String username,
            @Parameter(description = "真实姓名") @RequestParam(required = false) String realName) {
        Page<User> page = new Page<>(current, size);
        return Result.success(userService.page(page, null)); // 这里需要完善查询条件
    }

    @Operation(summary = "获取当前用户信息")
    @GetMapping("/current")
    public Result<UserInfoDTO> getCurrentUserInfo() {
        // 获取当前用户ID
        Long userId = tokenUtils.getCurrentUserId();
        if (userId == null) {
            return Result.error(401, "未登录或登录已过期");
        }
        
        // 获取用户信息
        return Result.success(userService.getUserInfo(userId));
    }

    @Operation(summary = "用户登出")
    @PostMapping("/logout")
    public Result<Boolean> logout() {
        return Result.success(userService.logout());
    }
}