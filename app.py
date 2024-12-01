import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import requests  # type: ignore # Necesitarás instalar requests con pip install requests
        
# Configuración de la ventana principal
root = tk.Tk()
root.title("Bienvenido al Sistema de Gestión de Inventario")
root.state("zoomed")  # Ocupa toda la pantalla

# Evento para ajustar la tabla al tamaño de la ventana
def ajustar_columnas(event):
    tabla.column("ID", width=int(root.winfo_width() * 0.1))
    tabla.column("Nombre", width=int(root.winfo_width() * 0.3))
    tabla.column("Cantidad", width=int(root.winfo_width() * 0.2))
    tabla.column("Precio Unitario", width=int(root.winfo_width() * 0.2))

# Función para cargar datos desde la API y mostrarlos en la tabla
def cargar_datos():
    try:
        response = requests.get("http://localhost:8080/productos")
        response.raise_for_status()  # Verifica si la solicitud fue exitosa
        productos = response.json()  # Obtiene los datos en formato JSON
        
        # Limpiar la tabla antes de agregar nuevos datos
        for row in tabla.get_children():
            tabla.delete(row)

        # Agregar cada producto a la tabla
        for producto in productos:
            tabla.insert("", "end", values=(producto["id"], producto["nombre"], producto["cantidad"], producto["Precio_Unitario"]))
    
    except requests.exceptions.RequestException as e:
        print("Error al cargar los datos:", e)

def agregar_producto():
    # Crear una ventana modal con un tamaño mayor
    ventana = tk.Toplevel()
    ventana.title("Agregar producto")
    ventana.geometry("350x250")  # Aumentamos el tamaño de la ventana
    ventana.transient()  # Evita que se interactúe con la ventana principal
    ventana.grab_set()   # Asegura que esta sea la ventana activa

    # Campo de entrada para el nombre del producto
    tk.Label(ventana, text="Nombre del producto:").pack(anchor="w", padx=10, pady=5)
    entry_nombre = tk.Entry(ventana)
    entry_nombre.pack(fill="x", padx=10, pady=5)

    # Campo de entrada para la cantidad
    tk.Label(ventana, text="Cantidad del producto:").pack(anchor="w", padx=10, pady=5)
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.pack(fill="x", padx=10, pady=5)

    # Campo de entrada para el precio unitario
    tk.Label(ventana, text="Precio unitario:").pack(anchor="w", padx=10, pady=5)
    entry_precio_unitario = tk.Entry(ventana)
    entry_precio_unitario.pack(fill="x", padx=10, pady=5)

    # Función para manejar la acción de guardar el producto
    def guardar_producto():
        nombre = entry_nombre.get()
        if not nombre:
            messagebox.showerror("Error", "El nombre del producto es obligatorio.")
            return

        try:
            cantidad = int(entry_cantidad.get())
            precio_unitario = float(entry_precio_unitario.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad o precio inválidos.")
            return

        # Datos del nuevo producto
        nuevo_producto = {
            "nombre": nombre,
            "cantidad": cantidad,
            "Precio_Unitario": precio_unitario
        }

        # Enviar solicitud al backend para agregar el producto
        try:
            response = requests.post("http://localhost:8080/productos", json=nuevo_producto)
            response.raise_for_status()
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            cargar_datos()  # Actualiza la lista de productos en tiempo real
            ventana.destroy()  # Cierra la ventana después de guardar

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")

    # Botón "OK" para guardar el producto
    boton_ok = tk.Button(ventana, text="OK", command=guardar_producto)
    boton_ok.pack(pady=10)

# Función para eliminar un producto
def eliminar_producto():
    # Solicita el ID del producto
    producto_id = simpledialog.askstring("Eliminar producto", "Ingrese el ID del producto a eliminar:")

    if producto_id is None:
        return  # Canceló el diálogo

    # Verificar que el ID ingresado sea numérico
    if not producto_id.isdigit():
        messagebox.showerror("Error", "ID inválido. Ingrese un número.")
        return

    producto_id = int(producto_id)

    # Obtener datos del producto para confirmar
    try:
        response = requests.get(f"http://localhost:8080/productos")
        response.raise_for_status()
        productos = response.json()

        producto = next((p for p in productos if p["id"] == producto_id), None)
        if not producto:
            messagebox.showerror("Error", "Producto no encontrado.")
            return

        # Muestra los detalles del producto
        detalles = f"ID: {producto['id']}\nNombre: {producto['nombre']}\nCantidad: {producto['cantidad']}\nPrecio Unitario: {producto['Precio_Unitario']}"
        confirm = messagebox.askyesno("Confirmar eliminación", f"¿Desea eliminar el siguiente producto?\n\n{detalles}")

        if confirm:
            # Enviar solicitud para eliminar
            response = requests.delete(f"http://localhost:8080/productos/{producto_id}")
            
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
                cargar_datos()  # Actualiza la lista de productos en tiempo real
            else:
                # Mostrar mensaje de error si falla la eliminación
                messagebox.showerror("Error", f"No se pudo eliminar el producto: {response.status_code} {response.text}")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")


    
# Función para editar un producto
def editar_producto():
    item_seleccionado = tabla.selection()
    if not item_seleccionado:
        messagebox.showerror("Error", "Seleccione un producto para editar.")
        return

    # Obtener los datos del producto seleccionado
    item = tabla.item(item_seleccionado)
    producto = item['values']

    ventana = tk.Toplevel()
    ventana.title("Editar producto")
    ventana.geometry("350x250")
    ventana.transient()
    ventana.grab_set()

    # Campos de entrada pre-rellenados
    tk.Label(ventana, text="Nombre del producto:").pack(anchor="w", padx=10, pady=5)
    entry_nombre = tk.Entry(ventana)
    entry_nombre.insert(0, producto[1])
    entry_nombre.pack(fill="x", padx=10, pady=5)

    tk.Label(ventana, text="Cantidad del producto:").pack(anchor="w", padx=10, pady=5)
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.insert(0, producto[2])
    entry_cantidad.pack(fill="x", padx=10, pady=5)

    tk.Label(ventana, text="Precio unitario:").pack(anchor="w", padx=10, pady=5)
    entry_precio_unitario = tk.Entry(ventana)
    entry_precio_unitario.insert(0, producto[3])
    entry_precio_unitario.pack(fill="x", padx=10, pady=5)

    def guardar_cambios():
        nombre = entry_nombre.get()
        if not nombre:
            messagebox.showerror("Error", "El nombre del producto es obligatorio.")
            return

        try:
            cantidad = int(entry_cantidad.get())
            precio_unitario = float(entry_precio_unitario.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad o precio inválidos.")
            return

        producto_editado = {
            "nombre": nombre,
            "cantidad": cantidad,
            "Precio_Unitario": precio_unitario
        }

        try:
            response = requests.put(f"http://localhost:8080/productos/{producto[0]}", json=producto_editado)
            response.raise_for_status()
            messagebox.showinfo("Éxito", "Producto editado correctamente.")
            cargar_datos()
            ventana.destroy()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"No se pudo editar el producto: {e}")

    boton_ok = tk.Button(ventana, text="Guardar", command=guardar_cambios)
    boton_ok.pack(pady=10)

# Etiqueta de título
label = tk.Label(root, text="Bienvenido al Sistema de Gestión de Inventario", font=("Arial", 18))
label.pack(pady=10)

# Marco para la tabla
tabla_frame = tk.Frame(root)
tabla_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Configuración de la tabla (sin datos de base de datos, solo estructura)
tabla = ttk.Treeview(tabla_frame, columns=("ID", "Nombre", "Cantidad", "Precio Unitario"), show="headings")
tabla.heading("ID", text="ID")
tabla.heading("Nombre", text="Nombre")
tabla.heading("Cantidad", text="Cantidad")
tabla.heading("Precio Unitario", text="Precio Unitario")

# Configuración inicial del ancho de columnas
tabla.column("ID", anchor="center")
tabla.column("Nombre", anchor="center")
tabla.column("Cantidad", anchor="center")
tabla.column("Precio Unitario", anchor="center")

# Barra de desplazamiento
scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
tabla.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tabla.pack(fill="both", expand=True)

# Asociar evento de redimensionamiento
root.bind("<Configure>", ajustar_columnas)

# Marco para los botones de acción
boton_frame = tk.Frame(root)
boton_frame.pack(pady=20)

# Botones y su configuración de comando
btn_agregar = tk.Button(boton_frame, text="Agregar", width=10, command=agregar_producto)
btn_agregar.grid(row=0, column=0, padx=10)

btn_editar = tk.Button(boton_frame, text="Editar", width=10, command=editar_producto)
btn_editar.grid(row=0, column=1, padx=10)

btn_eliminar = tk.Button(boton_frame, text="Eliminar", width=10, command=eliminar_producto)
btn_eliminar.grid(row=0, column=2, padx=10)

# Cargar datos automáticamente al iniciar
cargar_datos()

# Ejecutar la interfaz
root.mainloop()