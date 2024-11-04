package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"strconv"

	_ "github.com/denisenkom/go-mssqldb" // Paquete para conectarse a SQL Server
	"github.com/gin-gonic/gin"
)

func main() {
	// Conectar a la base de datos
	db, err := conectarBaseDeDatos()
	if err != nil {
		log.Fatal("Error al conectar a la base de datos:", err)
	}
	defer db.Close()

	// Configuración de rutas y servidor
	router := gin.Default()

	// Ruta para obtener la lista de productos
	router.GET("/productos", func(c *gin.Context) {
		productos, err := obtenerProductos(db)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error al obtener productos"})
			return
		}
		c.JSON(http.StatusOK, productos)
	})

	// Ruta para agregar un nuevo producto
	router.POST("/productos", func(c *gin.Context) {
		var producto struct {
			Nombre         string  `json:"nombre"`
			Cantidad       int     `json:"cantidad"`
			PrecioUnitario float64 `json:"Precio_Unitario"`
		}

		if err := c.BindJSON(&producto); err != nil {
			log.Println("Error en los datos JSON:", err)
			c.JSON(http.StatusBadRequest, gin.H{"error": "Datos inválidos"})
			return
		}

		if producto.Nombre == "" || producto.Cantidad < 0 || producto.PrecioUnitario < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Datos inválidos o incompletos"})
			return
		}

		newID, err := agregarProducto(db, producto.Nombre, producto.Cantidad, producto.PrecioUnitario)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error al insertar producto"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"message": "Producto agregado correctamente",
			"id":      newID,
		})
	})

	// Ruta para actualizar un producto existente
	router.PUT("/productos/:id", func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "ID inválido"})
			return
		}

		var producto struct {
			Nombre         string  `json:"nombre"`
			Cantidad       int     `json:"cantidad"`
			PrecioUnitario float64 `json:"Precio_Unitario"`
		}

		if err := c.BindJSON(&producto); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Datos inválidos"})
			return
		}

		if producto.Nombre == "" || producto.Cantidad < 0 || producto.PrecioUnitario < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Datos inválidos o incompletos"})
			return
		}

		err = actualizarProducto(db, id, producto.Nombre, producto.Cantidad, producto.PrecioUnitario)
		if err != nil {
			if err == sql.ErrNoRows {
				c.JSON(http.StatusNotFound, gin.H{"error": "Producto no encontrado"})
			} else {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Error al actualizar producto"})
			}
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Producto actualizado correctamente"})
	})

	// Ruta para eliminar un producto
	router.DELETE("/productos/:id", func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "ID inválido"})
			return
		}

		err = eliminarProducto(db, id)
		if err != nil {
			if err == sql.ErrNoRows {
				c.JSON(http.StatusNotFound, gin.H{"error": "Producto no encontrado"})
			} else {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Error al eliminar producto"})
			}
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Producto eliminado correctamente"})
	})

	// Iniciar el servidor en el puerto 8080
	router.Run(":8080")
}

// Función para conectar a la base de datos
func conectarBaseDeDatos() (*sql.DB, error) {
	connString := "server=localhost;user id=sa;password=uide.asu.123;database=INVENTARIO_DB;encrypt=disable"
	db, err := sql.Open("sqlserver", connString)
	if err != nil {
		return nil, err
	}

	if err := db.Ping(); err != nil {
		return nil, err
	}
	fmt.Println("Conexión a SQL Server exitosa!")
	return db, nil
}

// Función para obtener productos
func obtenerProductos(db *sql.DB) ([]map[string]interface{}, error) {
	rows, err := db.Query("SELECT id, nombre, cantidad, Precio_Unitario FROM productos")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var productos []map[string]interface{}
	for rows.Next() {
		var id int
		var nombre string
		var cantidad int
		var precioUnitario float64
		if err := rows.Scan(&id, &nombre, &cantidad, &precioUnitario); err != nil {
			return nil, err
		}
		productos = append(productos, gin.H{
			"id":              id,
			"nombre":          nombre,
			"cantidad":        cantidad,
			"Precio_Unitario": precioUnitario,
		})
	}
	return productos, nil
}

func agregarProducto(db *sql.DB, nombre string, cantidad int, precioUnitario float64) (int, error) {
	query := "INSERT INTO productos (nombre, cantidad, Precio_Unitario) VALUES (@nombre, @cantidad, @precio); SELECT CAST(SCOPE_IDENTITY() AS int)"
	var newID int
	err := db.QueryRow(query,
		sql.Named("nombre", nombre),
		sql.Named("cantidad", cantidad),
		sql.Named("precio", precioUnitario),
	).Scan(&newID)
	if err != nil {
		return 0, fmt.Errorf("error al escanear ID de producto: %w", err)
	}
	return newID, nil
}

// Función para actualizar un producto
func actualizarProducto(db *sql.DB, id int, nombre string, cantidad int, precioUnitario float64) error {
	query := "UPDATE productos SET nombre = @nombre, cantidad = @cantidad, Precio_Unitario = @precio WHERE id = @id"
	result, err := db.Exec(query,
		sql.Named("nombre", nombre),
		sql.Named("cantidad", cantidad),
		sql.Named("precio", precioUnitario),
		sql.Named("id", id),
	)
	if err != nil {
		return err
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rowsAffected == 0 {
		return sql.ErrNoRows
	}

	return nil
}

// Función para eliminar un producto
func eliminarProducto(db *sql.DB, id int) error {
	result, err := db.Exec("DELETE FROM productos WHERE id = @id", sql.Named("id", id))
	if err != nil {
		return err
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rowsAffected == 0 {
		return sql.ErrNoRows
	}

	return nil
}
