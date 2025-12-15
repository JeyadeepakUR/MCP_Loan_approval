"""
Flask Web Application for BFSI Loan Origination System
"""
from flask import Flask, render_template, request, jsonify, send_file
import uuid
from datetime import datetime

from agents.master_agent import MasterAgent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bfsi-loan-origination-secret-key'

# Store active sessions in memory (in production, use Redis/database)
active_sessions = {}


@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')


@app.route('/api/start-session', methods=['POST'])
def start_session():
    """Start a new loan application session"""
    session_id = str(uuid.uuid4())
    
    # Create new Master Agent instance for this session
    master = MasterAgent()
    welcome_message = master.start_conversation()
    
    # Store session
    active_sessions[session_id] = {
        'master_agent': master,
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'session_id': session_id,
        'message': welcome_message
    })


@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Process user message and return system response"""
    data = request.json
    session_id = data.get('session_id')
    user_message = data.get('message', '').strip()
    
    if not session_id or session_id not in active_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Get Master Agent for this session
    session = active_sessions[session_id]
    master = session['master_agent']
    
    # Process message
    try:
        response = master.process_message(user_message)
        
        # Get current state
        state = master.state_manager.load_state(master.current_session_id)
        
        return jsonify({
            'message': response,
            'stage': state.current_stage if state else 'UNKNOWN',
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({
            'error': f'Error processing message: {str(e)}'
        }), 500


@app.route('/api/session-summary/<session_id>', methods=['GET'])
def get_session_summary(session_id):
    """Get summary of a session"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = active_sessions[session_id]
    master = session['master_agent']
    summary = master.get_session_summary()
    
    return jsonify(summary)


@app.route('/api/download-sanction/<session_id>', methods=['GET'])
def download_sanction_letter(session_id):
    """Download sanction letter PDF"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = active_sessions[session_id]
    master = session['master_agent']
    state = master.state_manager.load_state(master.current_session_id)
    
    if not state or not state.sanction_letter_path:
        return jsonify({'error': 'Sanction letter not generated'}), 404
    
    return send_file(
        state.sanction_letter_path,
        as_attachment=True,
        download_name=f'sanction_letter_{state.customer_id}.pdf'
    )


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(active_sessions),
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("=" * 60)
    print("BFSI LOAN ORIGINATION SYSTEM - WEB UI")
    print("=" * 60)
    print("\n🚀 Starting server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("\n💡 Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
