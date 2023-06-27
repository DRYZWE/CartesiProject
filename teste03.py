from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)

# Dicionário para armazenar os dados de aluguel de bicicletas
bike_data = {
    'bike_id': None,
    'user_id': None,
    'start_time': None,
    'end_time': None,
    'rental_time': None,
    'transaction_hash': None
}

# Função para calcular o hash da transação
def calculate_transaction_hash(data):
    data_string = str(data['bike_id']) + str(data['user_id']) + str(data['rental_time']) + str(data['remaining_time'])
    return hashlib.sha256(data_string.encode()).hexdigest()

# Rota para alugar uma bicicleta
@app.route('/alugar', methods=['POST'])
def alugar_bicicleta():
    data = request.get_json()
    
    bike_id = data['bike_id']
    user_id = data['user_id']
    rental_time = int(data['rental_time'])
    
    # Verifica se a bicicleta já está alugada
    if bike_data['bike_id'] is not None:
        return jsonify({'message': 'Bicicleta já alugada'}), 400
    
    # Define os dados de aluguel da bicicleta
    bike_data['bike_id'] = bike_id
    bike_data['user_id'] = user_id
    bike_data['start_time'] = datetime.now()
    bike_data['rental_time'] = rental_time
    bike_data['transaction_hash'] = calculate_transaction_hash(data)
    
    return jsonify({'message': 'Bicicleta alugada com sucesso'})

# Rota para devolver uma bicicleta
@app.route('/devolver', methods=['POST'])
def devolver_bicicleta():
    if bike_data['bike_id'] is None:
        return jsonify({'message': 'Nenhuma bicicleta alugada'}), 400
    
    end_time = datetime.now()
    bike_data['end_time'] = end_time
    
    # Calcula o tempo restante caso o usuário não use todo o tempo alocado
    rental_time = bike_data['rental_time']
    used_time = (end_time - bike_data['start_time']).seconds // 60
    remaining_time = rental_time - used_time
    
    # Calcula o hash da transação
    transaction_data = {
        'bike_id': bike_data['bike_id'],
        'user_id': bike_data['user_id'],
        'rental_time': rental_time,
        'remaining_time': remaining_time
    }
    transaction_hash = calculate_transaction_hash(transaction_data)
    
    # Verifica se o hash da transação é válido
    if transaction_hash != bike_data['transaction_hash']:
        return jsonify({'message': 'Transação inválida'}), 400
    
    # Limpa os dados de aluguel da bicicleta
    bike_data['bike_id'] = None
    bike_data['user_id'] = None
    bike_data['start_time'] = None
    bike_data['end_time'] = None
    bike_data['rental_time'] = None
    bike_data['transaction_hash'] = None
    
    return jsonify({'message': 'Bicicleta devolvida com sucesso', 'remaining_time': remaining_time})

# Executa a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True)
