param(
    [string]$Env = "dev",
    [switch]$All,
    [string]$Headless = "",
    [string]$Browser = "",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

if ($All) {
    python .\scripts\run_environment_tests.py --all @RemainingArgs
    return
}

$env:ENV = $Env
if ($Headless) {
    $env:HEADLESS = $Headless
}
if ($Browser) {
    $env:BROWSER = $Browser
}

python .\scripts\run_environment_tests.py --env $Env @RemainingArgs
