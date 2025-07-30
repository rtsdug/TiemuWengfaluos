# Tiemu 项目

[English](./readme.md)|中文

## 快速开始

### 1. 克隆仓库：

   ```sh
   git clone https://github.com/YezQiu/Tiemu.git
   cd Tiemu
   ```

   或者使用任何你喜欢的方式将整个项目下载到你的电脑上

### 2. 创建并激活虚拟环境：​​

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

### 3. 安装依赖项：

   ```sh
   pip install -r requirements.txt
   ```

### 4. 下载模型文件：​​

   - 从 modelscope(https://www.modelscope.cn/models/unsloth/Qwen3-0.6B-GGUF)或官方来源下载 Qwen3-0.6B-Q8_0.gguf模型文件
   - 将其放入 models文件夹中


### 5. ​运行项目：

   ```sh
   python main.py
   ```
## 注意事项

- models文件夹和大模型文件已被 git 忽略
- 如果遇到问题，请检查是否安装了所有依赖项以及模型文件是否存在
- 即使没有大语言模型，项目仍然可以运行
