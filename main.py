from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import threading
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:180400KKcc@localhost/mydatabase'
db = SQLAlchemy(app)

# Создаем семафор для блокировки
lock = threading.Semaphore()


# модель Round
class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    users_count = db.Column(db.Integer, default=0)


# модель User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    rounds_played = db.Column(db.Integer, default=0)


# модель CellLog
class CellLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    cell_number = db.Column(db.Integer)


# Функция для выбора ячейки на основе весов
def select_cell(round_id):
    weights = [20, 100, 45, 70, 15, 140, 20, 20, 140, 45]
    total_weight = sum(weights)
    rand_num = random.randint(1, total_weight)

    cumulative_weight = 0
    for i, weight in enumerate(weights):
        cumulative_weight += weight
        if rand_num <= cumulative_weight:
            cell_number = i + 1  # Номер ячейки (от 1 до 10)
            # Сохраняем лог выпадения ячейки в базе данных
            cell_log = CellLog(round_id=round_id, cell_number=cell_number)
            db.session.add(cell_log)
            db.session.commit()
            return cell_number


@app.route('/spin', methods=['GET'])
def spin_roulette():
    user_id = request.args.get('user_id')

    try:
        with db.session.begin_nested():
            # Проверяем, существует ли текущий раунд
            current_round = Round.query.order_by(Round.id.desc()).first()

            if current_round is None or current_round.users_count >= 10:
                # Создаем новый раунд, только если нет активных раундов
                new_round = Round()
                db.session.add(new_round)
                db.session.flush()  # Создаем новый раунд и сохраняем его ID
                round_id = new_round.id
            else:
                # Если есть активный раунд, используем его ID
                round_id = current_round.id

        # Обновляем статистику пользователя только один раз перед блокировкой семафора
        user = User.query.get(user_id)
        if user is None:
            user = User(id=user_id, rounds_played=1)
            db.session.add(user)
        elif user.rounds_played == 0:
            user.rounds_played = 1

        # Выбираем ячейку
        cell_number = select_cell(round_id)

        # Блокируем семафор для обновления состояния раунда
        with lock:
            # Проверяем снова, чтобы избежать добавления пользователя, если другой поток уже добавил его
            current_round = Round.query.get(round_id)
            if current_round.users_count >= 10:
                return jsonify({'message': 'Максимальное количество пользователей в раунде достигнуто'})

            # Добавляем пользователя к текущему раунду
            current_round.users_count += 1

            # Сохраняем изменения в базе данных только один раз
            db.session.commit()

        return jsonify({'cell_number': cell_number})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@app.route('/stats', methods=['GET'])
def get_stats():
    # Получаем количество пользователей в каждом раунде
    rounds = Round.query.all()
    user_counts = [(round.id, round.users_count) for round in rounds]

    # Получаем список самых активных пользователей
    active_users = User.query.order_by(User.rounds_played.desc()).limit(10)
    active_users_data = [{'id': user.id, 'rounds_played': user.rounds_played} for user in active_users]

    # Создаем словарь с двумя ключами
    response_data = {
        "active_users": active_users_data,
        "user_counts": user_counts
    }

    # Возвращаем словарь в формате JSON с ensure_ascii=False
    return json.dumps(response_data, ensure_ascii=False)



@app.route('/reset_stats', methods=['POST'])
def reset_stats():
    # Очистить данные о раундах
    db.session.query(Round).delete()

    # Обновить статистику пользователей
    db.session.query(User).update({"rounds_played": 0})

    # Зафиксировать изменения в базе данных
    db.session.commit()

    return jsonify({'message': 'Статистика сброшена'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
