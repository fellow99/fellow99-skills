# OpenRouter Image Generation Script (PowerShell)
# Usage: .\generate-image.ps1 -Prompt "<prompt>" [-Model "model"] [-AspectRatio "16:9"] [-ImageSize "2K"]
#
# Environment variables:
#   OPENROUTER_BASE_URL  - API base URL (default: https://openrouter.ai/api/v1)
#   OPENROUTER_API_KEY   - API key (required)
#   OPENROUTER_MODEL     - Model name (default: openai/gpt-5.4-image-2)
#
# Examples:
#   .\generate-image.ps1 -Prompt "A beautiful sunset over mountains"
#   .\generate-image.ps1 -Prompt "A futuristic city" -Model "google/gemini-2.5-flash-image" -AspectRatio "16:9" -ImageSize "2K"

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Prompt,

    [Parameter(Mandatory = $false, Position = 1)]
    [string]$Model = "",

    [Parameter(Mandatory = $false, Position = 2)]
    [string]$AspectRatio = "",

    [Parameter(Mandatory = $false, Position = 3)]
    [string]$ImageSize = ""
)

# ============================================================
# Configuration
# ============================================================
$BaseUrl = if ($env:OPENROUTER_BASE_URL) { $env:OPENROUTER_BASE_URL.TrimEnd('/') } else { "https://openrouter.ai/api/v1" }
$ApiKey = $env:OPENROUTER_API_KEY

if (-not $Model) {
    $Model = if ($env:OPENROUTER_MODEL) { $env:OPENROUTER_MODEL } else { "openai/gpt-5.4-image-2" }
}

# Validate API Key
if (-not $ApiKey) {
    Write-Host "Error: OPENROUTER_API_KEY is not set" -ForegroundColor Red
    Write-Host "Please set: `$env:OPENROUTER_API_KEY = `"sk-or-v1-xxx`""
    exit 1
}

# ============================================================
# Build request body
# ============================================================
$body = @{
    model = $Model
    messages = @(
        @{
            role = "user"
            content = $Prompt
        }
    )
    modalities = @("image", "text")
}

# Add image_config if specified
if ($AspectRatio -or $ImageSize) {
    $imageConfig = @{}
    if ($AspectRatio) {
        $imageConfig["aspect_ratio"] = $AspectRatio
    }
    if ($ImageSize) {
        $imageConfig["image_size"] = $ImageSize
    }
    $body["image_config"] = $imageConfig
}

$jsonBody = $body | ConvertTo-Json -Depth 5

# ============================================================
# Display info
# ============================================================
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "OpenRouter Image Generation" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl"
Write-Host "Model: $Model"
Write-Host "Prompt: $Prompt"
if ($AspectRatio) { Write-Host "Aspect Ratio: $AspectRatio" }
if ($ImageSize) { Write-Host "Image Size: $ImageSize" }
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Calling API..." -ForegroundColor Yellow
Write-Host ""

# ============================================================
# Execute API call
# ============================================================
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/chat/completions" -Method Post `
        -Headers @{
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $ApiKey"
        } `
        -Body $jsonBody `
        -TimeoutSec 1800 `
        -ErrorAction Stop
} catch {
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "API Request Failed" -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    exit 1
}

# ============================================================
# Parse response and save image
# ============================================================
if ($response.choices -and $response.choices[0].message.images) {
    $imageUrl = $response.choices[0].message.images[0].image_url.url

    if ($imageUrl) {
        # Extract base64 data (remove data:image/png;base64, prefix)
        if ($imageUrl -match '^data:image/[a-z]+;base64,(.+)$') {
            $base64Data = $Matches[1]
        } else {
            Write-Host "Error: Unexpected image URL format" -ForegroundColor Red
            Write-Host "URL prefix: $($imageUrl.Substring(0, [Math]::Min(50, $imageUrl.Length)))..."
            exit 1
        }

        # Generate filename with timestamp
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $outputFile = "generated_$timestamp.png"

        # Decode and save
        $imageBytes = [Convert]::FromBase64String($base64Data)
        [System.IO.File]::WriteAllBytes((Join-Path $PWD $outputFile), $imageBytes)

        Write-Host "======================================" -ForegroundColor Green
        Write-Host "Image generated successfully!" -ForegroundColor Green
        Write-Host "======================================" -ForegroundColor Green
        Write-Host "Saved to: $outputFile" -ForegroundColor Green
        Write-Host "======================================" -ForegroundColor Green
    } else {
        Write-Host "======================================" -ForegroundColor Red
        Write-Host "No image found in response" -ForegroundColor Red
        Write-Host "======================================" -ForegroundColor Red
        $response | ConvertTo-Json -Depth 5
        exit 1
    }
} elseif ($response.error) {
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "API Error" -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "Error: $($response.error.message)" -ForegroundColor Red
    exit 1
} else {
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "No image found in response" -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    $response | ConvertTo-Json -Depth 5
    exit 1
}
