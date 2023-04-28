import clingo
import json
from flask import Flask, render_template, request

#ASPの処理
def parse_program(program):
    #clingoの初期化
    control = clingo.Control()
    #基礎化
    control.add("base", [], program)
    control.ground([("base", [])])
    return control

#ASPの解の探索
def find_model(control):
    with control.solve(yield_=True) as handle:
        for model in handle:
            model_array = []
            for symbols in model.symbols(atoms=True):
                '''
                if symbols.name == "staff":
                    for arg in symbols.arguments:
                        s_size = max(s_size, int(str(arg)))
                elif symbols.name == "days":
                    for arg in symbols.arguments:
                        d_size = max(d_size, int(str(arg)))
                    print(d_size)
                '''
                # staff と days のサイズを出力
                if symbols.name in "assign":
                    n = int(str(symbols.arguments[0]))
                    d = int(str(symbols.arguments[1]))
                    s = int(str(symbols.arguments[2]))

                    model_int = [n, d, s]
                    model_array.append(model_int)

                    #一旦[3][day*staff]のサイズで配列を作成しソート（シフトの出力順を乱さないため）
                    #第二要素をソート
                    model_array.sort(key=lambda x: x[1])
                    #第一要素をソート
                    model_array.sort(key=lambda x: x[0])
                    print(len(model_array))
                    #配列をarray[n][d] = sに変換
                    
            return model_array
    return None

def resize_array(old_array):
    new_array = []
    staff_size = 6
    day_size = 5
    for i in range(staff_size):
        row = []
        for j in range(day_size):
            row.append(old_array[day_size*i+j][2])
        new_array.append(row)
    return new_array

#配列をHTML形式へ変換
def array_to_html(model_array):
    html = "<table>\n<thead>\n<tr>\n<th></th>\n"
    for i in range(1, len(model_array[0])+1):
        html += "<th>{}</th>\n".format(i)
    html += "</tr>\n</thead>\n<tbody>\n"
    for i, row in enumerate(model_array):
        html += "<tr>\n<td>{}</td>\n".format(i+1)
        for cell in row:
            html += "<td>{}</td>\n".format(cell)
        html += "</tr>\n"
    html += "</tbody>\n</table>"
    return html


""" 
これだと[[Number(2), Number(1), Number(1)]の出力になる
if symbols.name in "assign":
    model_array.append(symbols.arguments) 
"""

#ホーム画面の出力
def show_homepage():
    return render_template('index.html')

#エラー画面の出力
def show_error():
    return render_template('error.html')

#結果画面の出力
def show_result(model):
    return render_template('result.html', model=model)

# Flaskアプリケーションの作成
app = Flask(__name__)

@app.route('/')
def index():
    return show_homepage()

@app.route('/solve', methods=['POST'])
#ASPの解析
def solve():
    # フォームから入力されたASPを取得
    program = request.form['asp_program']
    # 解析し制御オブジェクトを取得
    control = parse_program(program)
    # 制御オブジェクトから解を探索
    model = find_model(control)
    #model, s_size, d_size = find_model(control)
    #[day][staff]のサイズの配列へ変換
    table_model = resize_array(model)
    
    # 得られたモデルの配列をHTMLの表形式へ変換する
    #html = array_to_html(model)
    # 解の存在により出力，それ以外エラー
    return show_result(table_model) 
    #if model else show_error()

#Flaskの実行
if __name__ == '__main__':
    app.run(debug=True)
