# Save this code as app.py (or any_name.py)
import streamlit as st
import subprocess
import os

# --- 配置 ---
# 更改为你实际的 TikTok 下载脚本的路径
# 如果 TikTokDownloader.py 和这个 app.py 在同一个文件夹，可以直接用 "TikTokDownloader.py"
TIKTOK_DOWNLOADER_SCRIPT = "TikTokDownloader.py"
# 默认下载文件夹，会尝试在用户的主目录下的 Downloads 文件夹中创建一个 TikTok_Downloads 子文件夹
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "TikTok_Downloads")

# --- Streamlit 界面 ---
st.set_page_config(page_title="TikTok 下载器", layout="centered")
st.title("🎬 TikTok 视频下载器 (Streamlit GUI)")

st.markdown("""
使用此工具下载 TikTok 视频。
**注意：** 此 GUI 依赖于一个外部的命令行下载脚本。请确保该脚本可以正常工作。
原 `JoeanAmier/TikTokDownloader` 项目作者已声明其不再维护且无法工作。
""")

# --- 输入元素 ---
url = st.text_input("🔗 输入 TikTok 视频/用户/挑战/音乐链接或ID:", placeholder="例如: https://www.tiktok.com/@username/video/123...")

# 下载模式选项 (根据你的下载脚本支持的模式进行调整)
# 格式: "用户友好的显示名称": "脚本使用的命令行参数值"
mode_options = {
    "单个视频 (默认)": "video",
    "用户主页所有视频": "user",
    "挑战下的视频": "challenge",
    "音乐ID下的视频": "music"
}
selected_display_mode = st.selectbox("⚙️ 选择下载模式:", list(mode_options.keys()))
script_mode_arg = mode_options[selected_display_mode] # 获取对应的脚本参数值

# 保存路径
st.write("📁 保存设置:")
# 尝试创建默认下载文件夹（如果不存在）
if not os.path.exists(DEFAULT_DOWNLOAD_DIR):
    try:
        os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)
        st.info(f"已自动创建默认下载文件夹: {DEFAULT_DOWNLOAD_DIR}")
    except Exception as e:
        st.warning(f"无法自动创建默认下载文件夹 {DEFAULT_DOWNLOAD_DIR}: {e}. 请手动输入有效路径。")

save_directory = st.text_input("选择或输入视频保存文件夹路径:", value=DEFAULT_DOWNLOAD_DIR)


# --- 下载按钮和逻辑 ---
if st.button("🚀 开始下载", type="primary"):
    # 输入验证
    if not url:
        st.error("❌ 请输入 TikTok 链接！")
    elif not save_directory or not os.path.isdir(save_directory): # 确保路径存在且是文件夹
        st.error(f"❌ 请输入一个有效的保存文件夹路径！ '{save_directory}' 不是一个有效的文件夹。")
    else:
        st.info(f"ℹ️ 准备下载: {url[:50]}...")
        st.info(f"模式: {selected_display_mode} (脚本参数: {script_mode_arg})")
        st.info(f"将保存到: {save_directory}")

        # 构建命令行指令
        # 确保你的 Python 解释器是 python 还是 python3
        # 假设原脚本支持 -o 或 --output 来指定输出目录
        command = [
            "python",  # 或者 "python3"
            TIKTOK_DOWNLOADER_SCRIPT,
            "-u", url,
            "-m", script_mode_arg,
            "-o", save_directory  # 假设脚本用 -o 指定输出目录
            # 如果你的脚本有其他参数，例如 --no-watermark，可以在这里添加
            # "--no-watermark" # 示例
        ]

        st.caption(f"执行命令: `{' '.join(command)}`") # 显示将要执行的命令

        try:
            # 使用 st.spinner 来显示加载状态
            with st.spinner('⏳ 下载处理中，请耐心等待... (可能需要一段时间)'):
                # 执行命令行脚本
                # `creationflags=subprocess.CREATE_NO_WINDOW` 仅在 Windows 上隐藏命令行窗口
                process_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8', # 尝试指定编码以避免乱码
                    creationflags=process_flags
                )
                # 设置超时（例如5分钟），以防进程卡死
                stdout, stderr = process.communicate(timeout=300)

            # 处理结果
            if process.returncode == 0:
                st.success("✅ 下载任务已提交或完成！")
                if stdout:
                    st.subheader("输出信息:")
                    st.text_area("stdout", stdout, height=150)
                if stderr: # 有些工具会把进度信息输出到 stderr
                    st.subheader("可能的警告或进度信息:")
                    st.text_area("stderr", stderr, height=100)
            else:
                st.error(f"❌ 下载失败。脚本返回错误码: {process.returncode}")
                if stdout:
                    st.subheader("输出信息:")
                    st.text_area("stdout", stdout, height=150)
                if stderr:
                    st.subheader("错误详情:")
                    st.text_area("stderr", stderr, height=150)

        except subprocess.TimeoutExpired:
            st.error("❌ 下载超时！进程已运行超过5分钟，已被终止。请检查链接或网络。")
            if process: # type: ignore
                process.kill() # 确保终止进程
                stdout, stderr = process.communicate() # 获取残留输出
                if stdout: st.text_area("超时前 stdout", stdout)
                if stderr: st.text_area("超时前 stderr", stderr)
        except FileNotFoundError:
            st.error(f"❌ 脚本文件未找到: '{TIKTOK_DOWNLOADER_SCRIPT}'. 请确保路径正确，并且 Python 解释器配置正确。")
        except Exception as e:
            st.error(f"❌ 执行下载时发生意外错误: {str(e)}")
            st.exception(e) # 打印完整的异常栈

st.markdown("---")
st.markdown("测试")

# app.py (你的 Streamlit 代码在前面)
# ... (你现有的 st.title, st.button 等代码) ...

# 在文件末尾添加以下代码：
if __name__ == '__main__':
    import os
    from streamlit.web import bootstrap # Streamlit 1.18.0+
    # 或者老版本可能是 from streamlit import cli as stcli (需要查阅你用的Streamlit版本)

    # 获取当前脚本的真实路径
    # 这对于 PyInstaller 打包后的程序尤其重要，因为它可能在临时目录中运行
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script_path = os.path.join(current_dir, os.path.basename(__file__))

    # 检查是否是被 PyInstaller 打包
    # `sys.frozen` 是 PyInstaller 设置的一个属性
    # `'_MEIPASS2' in os.environ` 也是一个常见的检查，但 sys.frozen 更通用
    import sys
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        # 如果是被打包的，直接尝试运行
        # 注意：这种方式下，你的 app.py 就“是”那个 Streamlit 应用的入口
        # 不需要再通过 streamlit run xxx.py 的形式调用
        # Streamlit 的 bootstrap 会处理它
        # 你可能需要确保 PyInstaller 打包了所有 Streamlit 的依赖
        print(f"Running in PyInstaller bundle. Main script: {main_script_path}")
        # Streamlit 的 bootstrap.run 需要脚本的绝对路径
        # 以及一个空的命令行参数列表和一个标志字典
        # 下面的 FLAGS 可能需要根据你的 Streamlit 版本调整
        # 对于 Streamlit 1.18+
        bootstrap.run(main_script_path, '', [], {})

        # 对于老版本 Streamlit，可能使用 stcli
        # from streamlit import cli as stcli
        # sys.argv = ["streamlit", "run", main_script_path, "--global.developmentMode=false"]
        # sys.exit(stcli.main())
    else:
        # 如果是直接通过 python app.py 运行（开发时），
        # 我们可以用 subprocess 来模拟 streamlit run app.py
        # 但通常开发时你会直接用 streamlit run app.py
        print("Running in development mode. Please use 'streamlit run app.py'")
        # 或者，如果你希望 `python app.py` 也能启动，可以这样做：
        # import subprocess
        # subprocess.run(["streamlit", "run", main_script_path])

