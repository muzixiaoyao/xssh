# xssh 安装和使用指南

## 安装

### 1. 克隆项目
```bash
git clone https://github.com/muzixiaoyao/xssh.git
cd xssh
```

### 2. 安装依赖
```bash
pip install -e .
```

### 3. 安装 sshpass（必需）

**macOS:**
```bash
brew install hudochenkov/sshpass/sshpass
```

**Ubuntu/Debian:**
```bash
sudo apt-get install sshpass
```

**CentOS/RHEL:**
```bash
sudo yum install sshpass
```

## 配置

### 1. 创建 hosts.csv
```bash
mkdir -p ~/.ssh
```

复制项目中的 `example_hosts.csv` 内容，创建 `~/.ssh/hosts.csv`:

```csv
host,port,user,password
192.168.1.1,22,root,Root@123
192.168.1.1,22,dev,Dev@123
10.10.10.5,2222,admin,Admin@456
```

### 2. 设置文件权限
```bash
chmod 600 ~/.ssh/hosts.csv
```

## 使用

### 标准用法
```bash
xssh root@192.168.1.1
```

### 指定端口
```bash
xssh root@192.168.1.1:2222
```

### 仅指定主机（交互式选择用户）
```bash
xssh 192.168.1.1
```

## 项目结构
```
xssh/
├── xssh/
│   ├── __init__.py      # 包初始化
│   ├── cli.py           # CLI 入口
│   ├── core.py          # 核心逻辑
│   ├── models.py        # 数据模型
│   ├── exceptions.py    # 自定义异常
│   ├── parser.py        # 参数解析
│   ├── hosts_manager.py # CSV 管理
│   ├── finder.py        # 主机查找
│   ├── selector.py      # 用户选择
│   └── ssh.py           # SSH 连接
├── pyproject.toml       # 项目配置
├── example_hosts.csv    # 示例配置
└── README.md           # 使用说明
```
