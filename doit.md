WEB APİSİNE BAĞLAMAK İÇİN
cd /Users/kappasutra/QUANTUM\ MEMORY/web_dashboard/quantum-dashboard && npx serve -s build -l 3000 --single

BACK
python -m quantum_memory_compiler.api --host 0.0.0.0 --port 5001


API SERVER
https://quantum-memory-api.loca.lt
python -m quantum_memory_compiler.api


lt --port 5001 --subdomain quantum-memory-api

API Configuration'a gidin: Dashboard'da "Configure" butonuna tıklayın
Custom API URL seçin ve ngrok URL'inizi girin:


quantum_api_config