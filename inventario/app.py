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
    ventana.geometry("400x300")  # Aumentamos el tamaño de la ventana para mayor comodidad
    ventana.transient()  # Evita que se interactúe con la ventana principal
    ventana.grab_set()   # Asegura que esta sea la ventana activa

    # Configuración de fuente
    fuente_label = ("Times New Roman", 12, "bold")
    fuente_entry = ("Times New Roman", 12)

    # Campo de entrada para el nombre del producto
    tk.Label(ventana, text="Nombre del producto:", font=fuente_label).pack(anchor="w", padx=15, pady=5)
    entry_nombre = tk.Entry(ventana, font=fuente_entry)
    entry_nombre.pack(fill="x", padx=15, pady=5)

    # Campo de entrada para la cantidad
    tk.Label(ventana, text="Cantidad del producto:", font=fuente_label).pack(anchor="w", padx=15, pady=5)
    entry_cantidad = tk.Entry(ventana, font=fuente_entry)
    entry_cantidad.pack(fill="x", padx=15, pady=5)

    # Campo de entrada para el precio unitario
    tk.Label(ventana, text="Precio unitario:", font=fuente_label).pack(anchor="w", padx=15, pady=5)
    entry_precio_unitario = tk.Entry(ventana, font=fuente_entry)
    entry_precio_unitario.pack(fill="x", padx=15, pady=5)

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

    # Frame para alinear los botones en una fila
    botones_frame = tk.Frame(ventana)
    botones_frame.pack(pady=10)

    # Botón para guardar el producto
    btn_guardar = tk.Button(
        botones_frame, 
        text="Guardar", 
        font=("Times New Roman", 12, "bold"), 
        bg="lightblue",  # Color de fondo del botón
        fg="black",      # Color del texto
        width=12, 
        command=guardar_producto
    )
    btn_guardar.pack(side="left", padx=10)

    # Botón para cerrar la ventana sin guardar
    btn_cancelar = tk.Button(
        botones_frame, 
        text="Cancelar", 
        font=("Times New Roman", 12, "bold"), 
        bg="salmon",     # Color de fondo del botón
        fg="black",      # Color del texto
        width=12, 
        command=ventana.destroy
    )
    btn_cancelar.pack(side="left", padx=10)

def eliminar_producto_backend(producto_id, ventana_confirmacion):
    try:
        # Enviar solicitud de eliminación
        response = requests.delete(f"http://localhost:8080/productos/{producto_id}")
        response.raise_for_status()

        # Verificar si la eliminación fue exitosa
        if response.status_code == 200:
            messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            cargar_datos()  # Actualiza la lista de productos
            ventana_confirmacion.destroy()  # Cierra la ventana de confirmación
        else:
            messagebox.showerror("Error", "No se pudo eliminar el producto. Código de error: " + str(response.status_code))
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")

def eliminar_producto():
    # Crear una ventana emergente para ingresar el ID del producto
    ventana = tk.Toplevel()
    ventana.title("Eliminar producto")
    ventana.geometry("400x200")  # Ajustando el tamaño de la ventana
    ventana.transient()  # Evita que se interactúe con la ventana principal
    ventana.grab_set()   # Asegura que esta sea la ventana activa

    # Configuración de fuente
    fuente_label = ("Times New Roman", 14, "bold")
    fuente_entry = ("Times New Roman", 14)

    # Campo de entrada para el ID del producto
    tk.Label(ventana, text="Ingrese el ID del producto a eliminar:", font=fuente_label).pack(anchor="w", padx=15, pady=10)
    entry_id = tk.Entry(ventana, font=fuente_entry)
    entry_id.pack(fill="x", padx=15, pady=10)

    # Función para manejar la confirmación de eliminación
    def confirmar_eliminacion():
        producto_id = entry_id.get()
        if not producto_id or not producto_id.isdigit():
            messagebox.showerror("Error", "ID inválido.")
            return

        producto_id = int(producto_id)

        try:
            # Obtener todos los productos
            response = requests.get(f"http://localhost:8080/productos")
            response.raise_for_status()
            productos = response.json()

            # Buscar el producto con el ID dado
            producto = next((p for p in productos if p["id"] == producto_id), None)
            if not producto:
                messagebox.showerror("Error", "Producto no encontrado.")
                return

            # Crear una ventana de confirmación personalizada
            ventana_confirmacion = tk.Toplevel()
            ventana_confirmacion.title("Confirmar eliminación")
            ventana_confirmacion.geometry("550x350")  # Ajustando tamaño de la ventana
            ventana_confirmacion.transient()  # Evita que se interactúe con la ventana principal
            ventana_confirmacion.grab_set()

            # Crear un marco para contener los detalles del producto
            frame_detalles = tk.Frame(ventana_confirmacion, padx=20, pady=10)
            frame_detalles.pack(padx=10, pady=10)

            # Etiqueta de confirmación
            tk.Label(frame_detalles, text="¿Seguro que desea eliminar el siguiente producto?", font=("Times New Roman", 16, "bold")).pack(pady=10)

            # Detalles del producto con un formato más claro
            detalles = f"ID: {producto['id']}\n\nNombre: {producto['nombre']}\n\nCantidad: {producto['cantidad']}\n\nPrecio Unitario: {producto['Precio_Unitario']}"
            
            # Etiqueta para mostrar los detalles
            tk.Label(frame_detalles, text=detalles, font=("Times New Roman", 14), justify="left").pack(pady=15)

            # Agregar una línea divisoria para separar los datos
            tk.Frame(ventana_confirmacion, height=2, bg="gray").pack(fill="x", pady=5)

            # Frame para los botones
            botones_frame = tk.Frame(ventana_confirmacion)
            botones_frame.pack(pady=10)

            # Botón para confirmar la eliminación
            btn_confirmar = tk.Button(
                botones_frame, 
                text="Sí, eliminar", 
                font=("Times New Roman", 14, "bold"), 
                bg="lightblue",  # Color de fondo
                fg="black",      # Color del texto
                width=15, 
                command=lambda: eliminar_producto_backend(producto_id, ventana_confirmacion)
            )
            btn_confirmar.pack(side="left", padx=5)

            # Botón para cancelar la eliminación
            btn_cancelar = tk.Button(
                botones_frame, 
                text="Cancelar", 
                font=("Times New Roman", 14, "bold"), 
                bg="salmon",     # Color de fondo
                fg="black",      # Color del texto
                width=12, 
                command=ventana_confirmacion.destroy
            )
            btn_cancelar.pack(side="left", padx=5)

            # Cerrar la ventana de ID y abrir la de confirmación
            ventana.destroy()  # Cierra la ventana de entrada de ID

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"No se pudo obtener el producto: {e}")

    # Frame para los botones de la ventana de entrada de ID
    botones_frame = tk.Frame(ventana)
    botones_frame.pack(pady=10)

    # Botón para confirmar la eliminación (que validará el ID)
    btn_confirmar = tk.Button(
        botones_frame, 
        text="Confirmar eliminación", 
        font=("Times New Roman", 14, "bold"), 
        bg="lightblue",  # Color de fondo
        fg="black",      # Color del texto
        width=20, 
        command=confirmar_eliminacion
    )
    btn_confirmar.pack(side="left", padx=10)

    # Botón para cancelar la eliminación (cierra la ventana de ID)
    btn_cancelar = tk.Button(
        botones_frame, 
        text="Cancelar", 
        font=("Times New Roman", 14, "bold"), 
        bg="salmon",     # Color de fondo
        fg="black",      # Color del texto
        width=12, 
        command=ventana.destroy
    )
    btn_cancelar.pack(side="left", padx=10)

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
    ventana.geometry("400x250")
    ventana.transient()
    ventana.grab_set()

    # Configuración de fuentes
    fuente_label = ("Times New Roman", 12, "bold")
    fuente_entry = ("Times New Roman", 12)

    # Campos de entrada pre-rellenados
    tk.Label(ventana, text="Nombre del producto:", font=fuente_label).grid(row=0, column=0, sticky="w", padx=15, pady=10)
    entry_nombre = tk.Entry(ventana, font=fuente_entry)
    entry_nombre.insert(0, producto[1])
    entry_nombre.grid(row=0, column=1, padx=15, pady=10, sticky="ew")

    tk.Label(ventana, text="Cantidad del producto:", font=fuente_label).grid(row=1, column=0, sticky="w", padx=15, pady=10)
    entry_cantidad = tk.Entry(ventana, font=fuente_entry)
    entry_cantidad.insert(0, producto[2])
    entry_cantidad.grid(row=1, column=1, padx=15, pady=10, sticky="ew")

    tk.Label(ventana, text="Precio unitario:", font=fuente_label).grid(row=2, column=0, sticky="w", padx=15, pady=10)
    entry_precio_unitario = tk.Entry(ventana, font=fuente_entry)
    entry_precio_unitario.insert(0, producto[3])
    entry_precio_unitario.grid(row=2, column=1, padx=15, pady=10, sticky="ew")

    # Hacer que la columna 1 se expanda con los campos de entrada
    ventana.grid_columnconfigure(1, weight=1)

    # Función para guardar los cambios
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

    # Botones para guardar cambios y cancelar, alineados uno al lado del otro
    frame_botones = tk.Frame(ventana)
    frame_botones.grid(row=3, column=0, columnspan=2, pady=15)

    boton_ok = tk.Button(
        frame_botones, 
        text="Guardar", 
        command=guardar_cambios, 
        font=("Times New Roman", 12, "bold"),
        bg="lightblue",  # Color de fondo
        fg="black",      # Color del texto
        width=15
    )
    boton_ok.grid(row=0, column=0, padx=10)

    boton_cancelar = tk.Button(
        frame_botones, 
        text="Cancelar", 
        command=ventana.destroy, 
        font=("Times New Roman", 12, "bold"),
        bg="salmon",  # Color de fondo
        fg="black",   # Color del texto
        width=15
    )
    boton_cancelar.grid(row=0, column=1, padx=10)

# Etiqueta de título
titulo = tk.Label(root, text="¡Bienvenido al Sistema de Gestión de Inventario!", 
                  font=("Times New Roman", 24, "bold"), fg="blue")  # Aumentamos el tamaño y cambiamos fuente
titulo.pack(pady=10)


# Función para buscar productos por término
def buscar_producto():
    termino_busqueda = entry_busqueda.get().strip().lower()
    if not termino_busqueda:
        cargar_datos()  # Si no hay término de búsqueda, carga todos los productos
        return
    
    try:
        url = f"http://localhost:8080/productos/buscar?q={termino_busqueda}"
        response = requests.get(url)
        response.raise_for_status()
        productos = response.json()

        # Limpiar la tabla antes de agregar productos filtrados
        for row in tabla.get_children():
            tabla.delete(row)

        # Agregar productos filtrados a la tabla
        if productos:
            for producto in productos:
                tabla.insert("", "end", values=(
                    producto["id"],
                    producto["nombre"],
                    producto["cantidad"],
                    producto["Precio_Unitario"]
                ))
        else:
            messagebox.showinfo("Sin resultados", "No se encontraron productos que coincidan con la búsqueda.")
    
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"No se pudieron buscar los datos: {e}")

# Marco para la barra de búsqueda
frame_busqueda = tk.Frame(root)
frame_busqueda.pack(pady=10)

entry_busqueda = tk.Entry(frame_busqueda, font=("Times New Roman", 14), width=50)
entry_busqueda.pack(side="left", padx=10)

btn_buscar = tk.Button(
    frame_busqueda,
    text="Buscar",
    font=("Times New Roman", 14),
    bg="lightblue",
    fg="black",
    command=buscar_producto
)
btn_buscar.pack(side="left", padx=5)

btn_recargar = tk.Button(
    frame_busqueda,
    text="Mostrar todos",
    font=("Times New Roman", 14),
    bg="lightgreen",
    fg="black",
    command=cargar_datos
)
btn_recargar.pack(side="left", padx=5)

# Marco para la tabla
tabla_frame = tk.Frame(root)
tabla_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Crear un estilo personalizado para el Treeview
style = ttk.Style()
style.configure("Treeview.Heading", font=("Times New Roman", 14, "bold"))  # Encabezados en Times New Roman
style.configure("Treeview", font=("Times New Roman", 12))  # Filas de datos

# Configuración de la tabla
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
btn_agregar = tk.Button(
    boton_frame, 
    text="Agregar", 
    font=("Times New Roman", 14, "bold"),
    bg="lightblue",
    fg="black",
    width=12,
    command=agregar_producto
)
btn_agregar.grid(row=0, column=0, padx=15, pady=10)

btn_editar = tk.Button(
    boton_frame, 
    text="Editar", 
    font=("Times New Roman", 14, "bold"), 
    bg="lightgreen",
    fg="black",
    width=12,
    command=editar_producto
)
btn_editar.grid(row=0, column=1, padx=15, pady=10)

btn_eliminar = tk.Button(
    boton_frame, 
    text="Eliminar", 
    font=("Times New Roman", 14, "bold"), 
    bg="salmon",
    fg="black",
    width=12,
    command=eliminar_producto
)
btn_eliminar.grid(row=0, column=2, padx=15, pady=10)


# Cargar datos automáticamente al iniciar
cargar_datos()

# Ejecutar la interfaz
root.mainloop()