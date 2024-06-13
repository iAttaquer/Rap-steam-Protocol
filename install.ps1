# https://wkhtmltopdf.org/downloads.html

$wkhtmltopdf = "C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
$installer = "wkhtmltox-0.12.6-1.mvsc2015-win64.exe"
$url = "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe"

if (!(Test-Path ./virt)) {
    py -m venv ./virt
}
virt/Scripts/activate
py -m pip install -r .\requirements.txt

if (!(Test-Path $wkhtmltopdf)) {
    echo "Downloading wkhtmltopdf..."
    Invoke-WebRequest -Uri $url -OutFile $installer
    Start-Process -FilePath $installer -ArgumentList "/S" -Wait
    if ((Test-Path $wkhtmltopdf)) {
        echo "Installation completed!"
    } else {
        echo "Installation failed!"
    }
    Remove-Item $installer
} else {
    echo "wkhtmltopdf is installed!"
}