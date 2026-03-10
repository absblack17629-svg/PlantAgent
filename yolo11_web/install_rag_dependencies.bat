@echo off
chcp 65001 >nul
echo ========================================
echo 安装 RAG 相关依赖
echo ========================================

echo.
echo 检测 Python 环境...
python --version
if errorlevel 1 (
    echo ❌ Python 未找到，请确保 Python 已安装并添加到 PATH
    pause
    exit /b 1
)

echo.
echo 1. 安装 langchain-huggingface...
python -m pip install langchain-huggingface==0.0.3
if errorlevel 1 (
    echo ⚠️ langchain-huggingface 安装失败，尝试不指定版本...
    python -m pip install langchain-huggingface
)

echo.
echo 2. 安装 sentence-transformers...
python -m pip install sentence-transformers==3.0.1
if errorlevel 1 (
    echo ⚠️ sentence-transformers 安装失败，尝试不指定版本...
    python -m pip install sentence-transformers
)

echo.
echo 3. 安装 faiss-cpu...
python -m pip install faiss-cpu==1.8.0
if errorlevel 1 (
    echo ⚠️ faiss-cpu 安装失败，尝试不指定版本...
    python -m pip install faiss-cpu
)

echo.
echo 4. 验证安装...
python -c "from langchain_huggingface import HuggingFaceEmbeddings; print('✅ langchain_huggingface 导入成功')" 2>nul
if errorlevel 1 (
    echo ⚠️ langchain_huggingface 导入失败，尝试备用方案...
    python -c "from langchain_community.embeddings import HuggingFaceEmbeddings; print('✅ 使用 langchain_community 备用方案')" 2>nul
)

python -c "import sentence_transformers; print('✅ sentence_transformers 导入成功')" 2>nul
if errorlevel 1 (
    echo ❌ sentence_transformers 导入失败
)

python -c "import faiss; print('✅ faiss 导入成功')" 2>nul
if errorlevel 1 (
    echo ❌ faiss 导入失败
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
pause
