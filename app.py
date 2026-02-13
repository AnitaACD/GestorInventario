from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_muy_segura_cambia_esto'

# Datos en memoria (se pierden al reiniciar)
productos = []          # lista de diccionarios
movimientos = []        # lista de movimientos
next_id = 1             # contador manual de IDs

@app.route('/')
def index():
    return render_template('index.html', productos=productos)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    global next_id
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        try:
            precio = float(request.form.get('precio', 0))
        except:
            precio = 0
        try:
            stock = int(request.form.get('stock', 0))
        except:
            stock = 0
        codigo = request.form.get('codigo', '').strip() or None

        if not nombre:
            flash('El nombre es obligatorio', 'danger')
            return redirect(url_for('agregar'))

        # Verificar si el código ya existe (si se puso)
        if codigo and any(p['codigo'] == codigo for p in productos):
            flash('Ese código ya está en uso', 'danger')
            return redirect(url_for('agregar'))

        nuevo_producto = {
            'id': next_id,
            'nombre': nombre,
            'descripcion': descripcion,
            'precio': precio,
            'stock': stock,
            'codigo': codigo
        }
        productos.append(nuevo_producto)
        next_id += 1

        flash('Producto agregado correctamente', 'success')
        return redirect(url_for('index'))

    return render_template('agregar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    producto = next((p for p in productos if p['id'] == id), None)
    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        producto['nombre'] = request.form.get('nombre', producto['nombre']).strip()
        producto['descripcion'] = request.form.get('descripcion', producto['descripcion']).strip()
        try:
            producto['precio'] = float(request.form.get('precio', producto['precio']))
        except:
            pass
        codigo_nuevo = request.form.get('codigo', producto['codigo'] or '').strip() or None

        # Verificar código duplicado
        if codigo_nuevo and codigo_nuevo != producto['codigo']:
            if any(p['codigo'] == codigo_nuevo for p in productos if p['id'] != id):
                flash('Ese código ya está en uso', 'danger')
                return redirect(url_for('editar', id=id))

        producto['codigo'] = codigo_nuevo

        flash('Producto actualizado', 'success')
        return redirect(url_for('index'))

    return render_template('editar.html', producto=producto)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    global productos
    productos = [p for p in productos if p['id'] != id]
    # También eliminamos movimientos relacionados
    global movimientos
    movimientos = [m for m in movimientos if m['producto_id'] != id]
    flash('Producto eliminado', 'warning')
    return redirect(url_for('index'))

@app.route('/movimiento/<int:id>', methods=['GET', 'POST'])
def movimiento(id):
    producto = next((p for p in productos if p['id'] == id), None)
    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            cantidad = int(request.form.get('cantidad', 0))
        except:
            flash('Cantidad inválida', 'danger')
            return redirect(url_for('movimiento', id=id))

        tipo = request.form.get('tipo', 'entrada')
        nota = request.form.get('nota', '').strip()

        if tipo == 'salida' and cantidad > producto['stock']:
            flash(f'No hay suficiente stock. Disponible: {producto["stock"]}', 'danger')
            return redirect(url_for('movimiento', id=id))

        # Actualizar stock
        if tipo == 'entrada':
            producto['stock'] += cantidad
        else:
            producto['stock'] -= cantidad

        # Registrar movimiento
        movimientos.append({
            'id': len(movimientos) + 1,
            'producto_id': id,
            'nombre': producto['nombre'],
            'tipo': tipo,
            'cantidad': cantidad,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'nota': nota
        })

        flash(f'Movimiento registrado: {tipo} de {cantidad}', 'success')
        return redirect(url_for('index'))

    return render_template('movimiento.html', producto=producto)

@app.route('/historial')
def historial():
    return render_template('historial.html', movimientos=movimientos)

if __name__ == '__main__':
    app.run(debug=True)