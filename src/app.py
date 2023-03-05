from os import path
from flask import  send_from_directory, Flask, render_template, request, app, url_for, redirect,flash, session,send_from_directory, current_app
from flask_mysqldb import MySQL

app = Flask(__name__)

import pandas as pd
import os
#Imebu_deploy_multi_filter_test
app.secret_key = 'f3167129525f2a20696b7de80ff37401c963b55871119ed7ddec510809d5fa5530fa40bdf5041484a52a3932a4cad6e542e3c5199ef4cca9aa7c7e52f69c3e76'

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1098741116'
app.config['MYSQL_DB'] = 'deploy_nata'
app.config['UPLOAD_FOLDER'] = '/archivos'

uploads_dir = os.path.join(app.instance_path, 'archivos')


#ahora vamos a inicializar una sesion es decir datos que guarda nuestro servidor para luego poder reutilizarlos
#en este caso lo vamos a guardar dentro de la memoria de la aplicacion
#con secret_key le decimos como va a ir protegida nuestra sesion
app.secret_key = 'mysecretkey'

mysql = MySQL(app)
#cada vez que un usuario entre a nuestra ruta principal vamos a devolverle algo es esta linea:

@app.route('/', methods=['GET'])
def Inicio():
    if request.method == 'GET':
        if session:
            print(session)
            return redirect(url_for('tablaConsulta'))
        else:
            flash('inicia sesion para continuar')
            return redirect(url_for('Login'))

@app.route('/login', methods=['GET','POST'])
def Login():
    if request.method == 'GET':
        if 'role' in session.keys():
            if 'juridica' == session['role']:
                return redirect(url_for('gestionJuridica'))
            elif 'gesDoc' ==session['role']:
                return redirect(url_for('tablaConsulta'))
        return render_template('form-login.html')

    if request.method == 'POST':
        if 'role' in session.keys():
            if 'juridica' == session['role']:
                return redirect(url_for('gestionJuridica'))
            elif 'gesDoc' ==session['role']:
                return redirect(url_for('tablaConsulta'))
        else:
            user = request.form['usuario']
            user_pass = request.form['password']
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT * FROM users WHERE numDoc='{user}' AND pass='{user_pass}'")
            data=cur.fetchall()
            if not data:
                flash('usuario o la contraseña erroneos')
                return render_template('form-login.html')
            else:
                session['role'] = data[0][4]
                session['Nombre'] = data[0][2]
                if 'juridica' == session['role']:
                    return redirect(url_for('gestionJuridica'))
                elif 'gestDoc' == session['role']:
                    return redirect(url_for('tablaConsulta'))   

@app.route('/logout')
def Logout():
    if session:
        session.pop('role')
        session.pop('Nombre')
        return redirect(url_for('Login'))   
    else:
        flash('por favor, inicia sesion')
        return redirect(url_for('Login'))


@app.route('/dashboard-gestion-documental', methods=['GET','POST'])
def tablaConsulta():
    if request.method == 'GET':
        if session:
            if 'gestDoc' == session['role']:
                role=session['role']
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM inventarioDoc")
                sel=cur.fetchall()
                return render_template('inventarioDocumen.html',role=role,sel=sel)
            elif 'juridica' == session['role']:
                return redirect(url_for('gestionJuridica'))
        else:
            flash('por favor inicia sesion')
            return render_template('form-login.html')
        

@app.route('/dashboard-gestion-documental/<id>', methods=['POST'])
def tablaConsultaPost(id):
    if request.method == 'POST':
        if session:
            if 'gestDoc' == session['role']:
                role=session['role']
                a = request.files['archivo']
                #print(a.read())
                try:
                    df = pd.read_excel(a)
                    cur = mysql.connection.cursor()
                    cols=['Norden','codigo','serie','fechaInicial','fechaFinal','Caja','Carpeta','Tomo','Nfolios','Soporte','freqConsulta','Notas','Observaciones']
                    df_cols=list(df.columns)
                    check=not sum([not (col==df_cols[i]) for i,col in enumerate(cols)])
                    if check:
                        df['dependencia']=id
                        values=df.values
                        sql="""
                        INSERT INTO inventarioDoc VALUES
                        """
                        sql+="".join([f"({row[0]},'{row[1]}','{row[2]}','{row[3]}','{row[4]}',{row[5]},{row[6]},{row[7]},{row[8]},'{row[9]}','{row[10]}','{row[11]}','{row[12]}','{row[13]}'),"
                        for row in values])[:-1]
                        cur.execute(sql)
                        mysql.connection.commit()
                        return redirect(url_for('tablaConsulta'))
                    else:
                        flash('archivo no valido, columnas invalidas')
                        return render_template('inventarioDocumen.html',role=role)
                except Exception as e:
                    print(e)
                    flash('archivo no valido')
                    return redirect(url_for('tablaConsulta'))
            elif 'juridica' == session['role']:
                return redirect(url_for('gestionJuridica'))
        else:
            flash('por favor inicia sesion')
            return redirect(url_for('Login'))

@app.route('/agregar-nuevo/<id>', methods=['GET','POST'])
def addNewDocument(id):
    if request.method == 'GET':
        if session:
            if 'gestDoc' == session['role']:
                role=session['role']
                return render_template('form-nuevo-documental.html',role=role,id=id)
            elif 'juridica' == session['role']:
                return redirect(url_for('gestionJuridica'))
        else:
            flash('por favor inicia sesion')
            return redirect(url_for('Login'))

    if request.method == 'POST':
        if session:
            if 'gestDoc' == session['role']:
                try:
                    cur = mysql.connection.cursor()
                    Norden = request.form['Norden']
                    Codigo = request.form['Codigo']
                    Serie =request.form['SerSubAsun']
                    FechaInicial = request.form['FechaInicial']
                    FechaFinal = request.form['FechaFinal']
                    Caja = request.form['Caja']
                    Carpeta = request.form['Carpeta']
                    Tomo = request.form['Tomo']
                    #OTROS
                    Nfolios = request.form['Nfolios']
                    Soporte = request.form['Soporte']
                    FrecuConsulta = request.form['FrecuConsulta']
                    Notas = request.form['Notas']
                    Observaciones = request.form['Observaciones']
                    #print(cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())
                    cur.execute(f"""insert into inventarioDoc values
                    ({Norden},'{Codigo}','{Serie}','{FechaInicial}','{FechaFinal}',{Caja},
                    {Carpeta},{Tomo}, {Nfolios},'{Soporte}','{FrecuConsulta}',
                    '{Notas}','{Observaciones}','{id}')""")
                    mysql.connection.commit()
                    return redirect(url_for('tablaConsulta'))
                except Exception as e:
                    print(e)
                    flash('Datos no validos')
                    return redirect(url_for('tablaConsulta'))
            elif 'juridica' == session['role']:
                return redirect(url_for('gestionJuridica'))
        else:
            flash('por favor inicia sesion')
            return redirect(url_for('Login'))


@app.route('/update-one/<dependencia>/<id>', methods=['GET','POST'])
def updateDocument(dependencia,id):
    if request.method == 'GET':
        if session:
            if 'gestDoc' == session['role']:
                role=session['role']
                cur = mysql.connection.cursor()
                cur.execute(f"SELECT * FROM inventarioDoc WHERE Norden={id} AND dependencia='{dependencia}'")
                data=cur.fetchall()[0]
                return render_template('form-edit-documental.html',data=data,role=role)
            elif 'juridica' == session['role']:
                return redirect(url_for('gestionJuridica'))
        else:
            flash('por favor inicia sesion')
            return redirect(url_for('Login'))

    if request.method == 'POST':
        if session:
            if 'gestDoc' == session['role']:
                cur = mysql.connection.cursor()
                Norden = request.form['Norden']
                Codigo = request.form['Codigo']
                Serie =request.form['SerSubAsun']
                FechaInicial = request.form['FechaInicial']
                FechaFinal = request.form['FechaFinal']
                Caja = request.form['Caja']
                Carpeta = request.form['Carpeta']
                Tomo = request.form['Tomo']
                #OTROS
                Nfolios = request.form['Nfolios']
                Soporte = request.form['Soporte']
                FrecuConsulta = request.form['FrecuConsulta']
                Notas = request.form['Notas']
                Observaciones = request.form['Observaciones']
                cur.execute(f"""UPDATE inventarioDoc SET
                Norden={Norden},codigo='{Codigo}',serie='{Serie}',fechaInicial='{FechaInicial}',
                fechaFinal='{FechaFinal}',Caja={Caja},Carpeta={Carpeta},Tomo={Tomo},
                Nfolios= {Nfolios},Soporte='{Soporte}',freqConsulta='{FrecuConsulta}',
                Notas='{Notas}',Observaciones='{Observaciones}',dependencia='{dependencia}'
                WHERE Norden={id} AND dependencia='{dependencia}'""")
                mysql.connection.commit()    
                return redirect(url_for('tablaConsulta'))
            elif 'juridica' == session['role']:
                return redirect(url_for('gestionJuridica'))
        else:
            flash('por favor inicia sesion')
            return redirect(url_for('Login'))


@app.route('/delete-one/<dependencia>/<id>', methods=['GET'])
def deleteDocument(dependencia,id):
    if request.method == 'GET':
        if session:
            if 'gestDoc' == session['role']:
                cur = mysql.connection.cursor()
                cur.execute(f"DELETE FROM inventarioDoc WHERE Norden ={id} AND dependencia='{dependencia}'")
                mysql.connection.commit()
                return redirect(url_for('tablaConsulta'))
            elif 'juridica' == session['role']:
                return redirect(url_for('gestionJuridica'))
        else:
            flash('por favor inicia sesion')
            return redirect(url_for('Login'))

############# juridica
@app.route('/gestion-juridica', methods=['GET'])
def gestionJuridica():
    if request.method == 'GET':
        if session:
            if 'juridica' == session['role']:
                role = session['role']
                cur = mysql.connection.cursor()
                cur.execute(f"SELECT * FROM gestJuridica")
                datos=cur.fetchall()
                return render_template('juridica.html',datos=datos,role=role)
            elif 'gestDoc' == session['role']:
                return redirect(url_for('tablaConsulta'))
        else:
            flash('por favor inicia sesion')
            return redirect(url_for('Login'))


@app.route('/gestion-juridica', methods=['POST'])
def gestionJuridicaPost():
    if request.method == 'POST':
        if session:
            if 'juridica' == session['role']:
                a = request.files['archivo']
                name = a.filename
                try:
                    cur = mysql.connection.cursor()
                    sql=f"""
                    INSERT INTO gestJuridica VALUES ('{name}')
                    """
                    cur.execute(sql)
                    mysql.connection.commit()
                    filename = name
                    file=a
                    file.save(os.path.join(uploads_dir, filename))
                    return redirect(url_for('gestionJuridica'))
                except Exception as e:
                    print(e)
                    flash('archivo no valido, o archivo ya registrado en la base de datos')
                    return redirect(url_for('gestionJuridica'))
            elif 'gestDoc' == session['role']:
                return redirect(url_for('tablaConsulta'))
        else:
            flash('por favor inicia sesion')
            return redirect(url_for('Login'))            

@app.route('/delete-juridica/<id>', methods=['GET'])
def deleteGestJuridica(id):
    if request.method == 'GET':
        if session:
            if 'juridica' == session['role']:
                cur = mysql.connection.cursor()
                cur.execute(f"DELETE FROM gestJuridica WHERE name ='{id}'")
                mysql.connection.commit()
                os.remove(os.path.join(uploads_dir, id))
                return redirect(url_for('gestionJuridica'))
            elif 'gestDoc' == session['role']:
                return redirect(url_for('tablaConsulta'))
        else:
            flash('por favor inicia sesion')
            return redirect(url_for('Login'))


@app.route('/vista-doc-juridica/<id>', methods=['GET'])
def vistaDocJuridica(id):
    if request.method == 'GET':
        if session:
            if 'juridica' == session['role']:
                role=session['role']
                name=id
                datos=pd.read_excel(os.path.join(uploads_dir, id))
                cols=list(datos.columns)
                datos=tuple([tuple(cols),*tuple([tuple(row) for row in datos.values])])
                return render_template('vista-doc-juridica.html',datos=datos,name=name,role=role)
            elif 'gestDoc' == session['role']:
                return redirect(url_for('tablaConsulta'))
        else:
            flash('por favor inicia sesion')
            return redirect(url_for('Login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
