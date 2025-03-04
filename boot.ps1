param (
    [string]$VAR_CONTEXT = "development"
)

if ($VAR_CONTEXT -eq "production") {
    $VAR_CONTEXT = "production"
} else {
    $VAR_CONTEXT = "development"
}

Write-Output "Environment set to: $VAR_CONTEXT"
$env:FLASK_CONTEXT = $VAR_CONTEXT
python app.py