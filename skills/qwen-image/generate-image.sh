#!/bin/bash
# 千问文生图 API 调用脚本
# 使用方式：./generate-image.sh "<prompt>" [model] [size] [n]

set -e

# 参数检查
if [ -z "$1" ]; then
    echo "用法：$0 \"<提示词>\" [模型] [分辨率] [数量]"
    echo "示例：$0 \"一只可爱的猫咪\" qwen-image-2.0-pro \"2048*2048\" 1"
    exit 1
fi

# 参数设置
PROMPT="$1"
MODEL="${2:-qwen-image-2.0-pro}"
SIZE="${3:-2048*2048}"
N="${4:-1}"

# 检查 API Key
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "错误：未设置环境变量 DASHSCOPE_API_KEY"
    echo "请执行：export DASHSCOPE_API_KEY=\"sk-xxx\""
    exit 1
fi

echo "======================================"
echo "千问文生图 API 调用"
echo "======================================"
echo "模型：$MODEL"
echo "分辨率：$SIZE"
echo "数量：$N"
echo "提示词：$PROMPT"
echo "======================================"

# 判断模型类型，选择调用方式
if [[ "$MODEL" == qwen-image* ]]; then
    # 千问系列 - 同步调用
    echo "调用方式：同步（千问系列）"
    
    RESPONSE=$(curl --silent --location \
        'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
        --header 'Content-Type: application/json' \
        --header "Authorization: Bearer $DASHSCOPE_API_KEY" \
        --data "{
            \"model\": \"$MODEL\",
            \"input\": {
                \"messages\": [
                    {
                        \"role\": \"user\",
                        \"content\": [
                            {
                                \"text\": \"$PROMPT\"
                            }
                        ]
                    }
                ]
            },
            \"parameters\": {
                \"negative_prompt\": \"低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感。构图混乱。文字模糊，扭曲。\",
                \"prompt_extend\": true,
                \"watermark\": false,
                \"size\": \"$SIZE\"
            }
        }")
    
    echo ""
    echo "响应："
    echo "$RESPONSE" | jq .
    
    # 提取图像 URL
    IMAGE_URL=$(echo "$RESPONSE" | jq -r '.output.choices[0].message.content[0].image // empty')
    
    if [ -n "$IMAGE_URL" ]; then
        echo ""
        echo "======================================"
        echo "✅ 生成成功！"
        echo "图像 URL: $IMAGE_URL"
        echo "⚠️  注意：URL 有效期 24 小时，请及时下载"
        echo "======================================"
    else
        echo ""
        echo "======================================"
        echo "❌ 生成失败"
        ERROR_CODE=$(echo "$RESPONSE" | jq -r '.code // "UNKNOWN"')
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.message // "未知错误"')
        echo "错误码：$ERROR_CODE"
        echo "错误信息：$ERROR_MSG"
        echo "======================================"
        exit 1
    fi

elif [[ "$MODEL" == wan* ]]; then
    # 万相系列 - 异步调用
    echo "调用方式：异步（万相系列）"
    
    # 步骤 1：创建任务
    echo "步骤 1/2: 创建任务..."
    
    CREATE_RESPONSE=$(curl --silent --location \
        'https://dashscope.aliyuncs.com/api/v1/services/aigc/image-generation/generation' \
        --header 'Content-Type: application/json' \
        --header "Authorization: Bearer $DASHSCOPE_API_KEY" \
        --header "X-DashScope-Async: enable" \
        --data "{
            \"model\": \"$MODEL\",
            \"input\": {
                \"messages\": [
                    {
                        \"role\": \"user\",
                        \"content\": [
                            {
                                \"text\": \"$PROMPT\"
                            }
                        ]
                    }
                ]
            },
            \"parameters\": {
                \"size\": \"${SIZE/2048*2048/2K}\",
                \"n\": $N,
                \"watermark\": false,
                \"thinking_mode\": true
            }
        }")
    
    TASK_ID=$(echo "$CREATE_RESPONSE" | jq -r '.output.task_id // empty')
    
    if [ -z "$TASK_ID" ]; then
        echo "❌ 任务创建失败"
        echo "$CREATE_RESPONSE" | jq .
        exit 1
    fi
    
    echo "任务 ID: $TASK_ID"
    echo "步骤 2/2: 等待任务完成..."
    
    # 步骤 2：轮询任务状态
    MAX_ATTEMPTS=40
    ATTEMPT=0
    
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        sleep 3
        
        STATUS_RESPONSE=$(curl --silent --location \
            "https://dashscope.aliyuncs.com/api/v1/tasks/$TASK_ID" \
            --header "Authorization: Bearer $DASHSCOPE_API_KEY")
        
        TASK_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.output.task_status // "UNKNOWN"')
        
        echo "  尝试 $((ATTEMPT + 1))/$MAX_ATTEMPTS - 状态：$TASK_STATUS"
        
        if [ "$TASK_STATUS" = "SUCCEEDED" ]; then
            echo ""
            echo "✅ 任务完成！"
            echo ""
            echo "响应："
            echo "$STATUS_RESPONSE" | jq .
            
            # 提取图像 URL（可能多个）
            IMAGE_URLS=$(echo "$STATUS_RESPONSE" | jq -r '.output.choices[].message.content[].image // empty')
            
            if [ -n "$IMAGE_URLS" ]; then
                echo ""
                echo "======================================"
                echo "生成的图像 URL:"
                echo "$IMAGE_URLS"
                echo ""
                echo "⚠️  注意：URL 有效期 24 小时，请及时下载"
                echo "======================================"
            fi
            exit 0
            
        elif [ "$TASK_STATUS" = "FAILED" ]; then
            echo ""
            echo "======================================"
            echo "❌ 任务失败"
            echo "$STATUS_RESPONSE" | jq .
            echo "======================================"
            exit 1
        fi
        
        ATTEMPT=$((ATTEMPT + 1))
    done
    
    echo ""
    echo "======================================"
    echo "❌ 任务超时（超过 $((MAX_ATTEMPTS * 3)) 秒）"
    echo "======================================"
    exit 1

else
    echo "错误：未知的模型类型 '$MODEL'"
    echo "支持的模型：qwen-image-* 或 wan*"
    exit 1
fi
