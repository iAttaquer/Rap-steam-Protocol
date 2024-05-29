if (!Test-Path./virt) {
    py -m venv ./virt
    virt/Scripts/activate
    py -m pip install -r .\requirements.txt
}
virt/Scripts/activate