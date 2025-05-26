WEB APİSİNE BAĞLAMAK İÇİN
cd /Users/kappasutra/QUANTUM\ MEMORY/web_dashboard/quantum-dashboard && npx serve -s build -l 3000 --single

BACK
python -m quantum_memory_compiler.api --host 0.0.0.0 --port 5001