# Install packages

cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
cd frontend
npm install
npm update
cd ..

# Initialize database

flask db init --directory backend/migrations
flask db migrate -m 'Initial Migration'
flask db upgrade
