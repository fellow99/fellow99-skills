#!/bin/bash
# opencode-api.sh - opencode REST API 命令行封装
# 用法：./opencode-api.sh <command> [args...]

# 配置
BASE_URL="${OPENCODE_SERVER_BASE_URL:-http://127.0.0.1:4096}"
USERNAME="${OPENCODE_SERVER_USERNAME:-opencode}"
PASSWORD="${OPENCODE_SERVER_PASSWORD:-}"

# 构建 curl 认证参数
auth_param=""
if [ -n "$PASSWORD" ]; then
  auth_param="-u ${USERNAME}:${PASSWORD}"
fi

# 辅助函数
api_get() {
  curl -s $auth_param "$BASE_URL$1"
}

api_post() {
  curl -s $auth_param -X POST "$BASE_URL$1" -H "Content-Type: application/json" -d "$2"
}

api_delete() {
  curl -s $auth_param -X DELETE "$BASE_URL$1"
}

api_patch() {
  curl -s $auth_param -X PATCH "$BASE_URL$1" -H "Content-Type: application/json" -d "$2"
}

# 命令处理
case "$1" in
  health)
    echo "=== 健康检查 ==="
    api_get "/global/health" | jq .
    ;;
  
  config)
    echo "=== 配置 ==="
    api_get "/config" | jq .
    ;;
  
  providers)
    echo "=== 可用提供商和模型 ==="
    api_get "/config/providers" | jq .
    ;;
  
  sessions)
    echo "=== 会话列表 ==="
    api_get "/session" | jq .
    ;;
  
  create-session)
    title="${2:-新会话}"
    echo "=== 创建会话：$title ==="
    api_post "/session" "{\"title\": \"$title\"}" | jq .
    ;;
  
  get-session)
    session_id="$2"
    if [ -z "$session_id" ]; then
      echo "用法：$0 get-session <session_id>"
      exit 1
    fi
    echo "=== 获取会话：$session_id ==="
    api_get "/session/$session_id" | jq .
    ;;
  
  delete-session)
    session_id="$2"
    if [ -z "$session_id" ]; then
      echo "用法：$0 delete-session <session_id>"
      exit 1
    fi
    echo "=== 删除会话：$session_id ==="
    api_delete "/session/$session_id" | jq .
    ;;
  
  messages)
    session_id="$2"
    limit="${3:-50}"
    if [ -z "$session_id" ]; then
      echo "用法：$0 messages <session_id> [limit]"
      exit 1
    fi
    echo "=== 获取消息 (limit=$limit) ==="
    api_get "/session/$session_id/message?limit=$limit" | jq .
    ;;
  
  send)
    session_id="$2"
    message="$3"
    if [ -z "$session_id" ] || [ -z "$message" ]; then
      echo "用法：$0 send <session_id> <message>"
      exit 1
    fi
    echo "=== 发送消息到 $session_id ==="
    api_post "/session/$session_id/message" "{\"parts\": [{\"type\": \"text\", \"text\": \"$message\"}]}" | jq .
    ;;
  
  abort)
    session_id="$2"
    if [ -z "$session_id" ]; then
      echo "用法：$0 abort <session_id>"
      exit 1
    fi
    echo "=== 中止会话：$session_id ==="
    api_post "/session/$session_id/abort" "{}" | jq .
    ;;
  
  projects)
    echo "=== 项目列表 ==="
    api_get "/project" | jq .
    ;;
  
  current-project)
    echo "=== 当前项目 ==="
    api_get "/project/current" | jq .
    ;;
  
  files)
    path="${2:-.}"
    echo "=== 文件列表：$path ==="
    api_get "/file?path=$path" | jq .
    ;;
  
  read-file)
    file_path="$2"
    if [ -z "$file_path" ]; then
      echo "用法：$0 read-file <path>"
      exit 1
    fi
    echo "=== 读取文件：$file_path ==="
    api_get "/file/content?path=$file_path" | jq .
    ;;
  
  search)
    pattern="$2"
    if [ -z "$pattern" ]; then
      echo "用法：$0 search <pattern>"
      exit 1
    fi
    echo "=== 搜索：$pattern ==="
    api_get "/find?pattern=$pattern" | jq .
    ;;
  
  find-files)
    query="$2"
    if [ -z "$query" ]; then
      echo "用法：$0 find-files <query>"
      exit 1
    fi
    echo "=== 查找文件：$query ==="
    api_get "/find/file?query=$query" | jq .
    ;;
  
  agents)
    echo "=== 可用代理 ==="
    api_get "/agent" | jq .
    ;;
  
  commands)
    echo "=== 可用命令 ==="
    api_get "/command" | jq .
    ;;
  
  skills)
    echo "=== 可用技能 ==="
    api_get "/skill" | jq .
    ;;
  
  mcp)
    echo "=== MCP 服务器状态 ==="
    api_get "/mcp" | jq .
    ;;
  
  *)
    echo "opencode-api - opencode REST API 命令行封装"
    echo ""
    echo "用法：$0 <command> [args...]"
    echo ""
    echo "命令:"
    echo "  health              健康检查"
    echo "  config              获取配置"
    echo "  providers           获取提供商和模型列表"
    echo "  sessions            列出所有会话"
    echo "  create-session [title]  创建新会话"
    echo "  get-session <id>    获取会话详情"
    echo "  delete-session <id> 删除会话"
    echo "  messages <id> [limit] 获取消息列表"
    echo "  send <id> <message> 发送消息"
    echo "  abort <id>          中止会话"
    echo "  projects            列出项目"
    echo "  current-project     获取当前项目"
    echo "  files [path]        列出文件"
    echo "  read-file <path>    读取文件内容"
    echo "  search <pattern>    搜索文本"
    echo "  find-files <query>  查找文件"
    echo "  agents              列出可用代理"
    echo "  commands            列出可用命令"
    echo "  skills              列出可用技能"
    echo "  mcp                 MCP 服务器状态"
    echo ""
    echo "环境变量:"
    echo "  OPENCODE_SERVER_BASE_URL   API 基础 URL (默认：http://127.0.0.1:4096)"
    echo "  OPENCODE_SERVER_USERNAME   用户名 (默认：opencode)"
    echo "  OPENCODE_SERVER_PASSWORD   密码 (如果服务器启用了认证)"
    exit 1
    ;;
esac
