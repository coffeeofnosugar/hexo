# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit

# 确保在 Git 仓库目录中运行
if [ -d ".git" ]; then
    echo "当前路径: $(pwd)"
    git pull
else
    echo "错误：未找到 Git 仓库"
    exit 1
fi


git pull
python3 ./source/_posts/combine_exercise3.0.py
hexo cl && hexo g
