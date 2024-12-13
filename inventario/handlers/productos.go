package handlers

import (
	"database/sql"
	"net/http"
	"strconv"

	"inventario/models"

	"github.com/gin-gonic/gin"
)

// RegistrarRutasProductos registra las rutas relacionadas con productos
func RegistrarRutasProductos(router *gin.Engine, db *sql.DB) {
	router.GET("/productos", func(c *gin.Context) {
		productos, err := ObtenerProductos(db)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error al obtener productos"})
			return
		}
		c.JSON(http.StatusOK, productos)
	})

	router.GET("/productos/buscar", func(c *gin.Context) {
		termino := c.Query("q") // Obtener el parámetro de búsqueda de la query string
		if termino == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "El término de búsqueda no puede estar vacío"})
			return
		}

		productos, err := BuscarProductos(db, termino)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error al buscar productos"})
			return
		}

		c.JSON(http.StatusOK, productos)
	})

	router.POST("/productos", func(c *gin.Context) {
		var producto models.Producto
		if err := c.BindJSON(&producto); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Datos inválidos"})
			return
		}

		newID, err := AgregarProducto(db, producto.Nombre, producto.Cantidad, producto.PrecioUnitario)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error al agregar producto"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"message": "Producto agregado correctamente",
			"id":      newID,
		})
	})

	router.PUT("/productos/:id", func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "ID inválido"})
			return
		}

		var producto models.Producto
		if err := c.BindJSON(&producto); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Datos inválidos"})
			return
		}

		err = ActualizarProducto(db, id, producto.Nombre, producto.Cantidad, producto.PrecioUnitario)
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

	router.DELETE("/productos/:id", func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "ID inválido"})
			return
		}

		err = EliminarProducto(db, id)
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
}

// Funciones auxiliares
func ObtenerProductos(db *sql.DB) ([]models.Producto, error) {
	rows, err := db.Query("SELECT id, nombre, cantidad, Precio_Unitario FROM productos")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var productos []models.Producto
	for rows.Next() {
		var p models.Producto
		if err := rows.Scan(&p.ID, &p.Nombre, &p.Cantidad, &p.PrecioUnitario); err != nil {
			return nil, err
		}
		productos = append(productos, p)
	}
	return productos, nil
}

func AgregarProducto(db *sql.DB, nombre string, cantidad int, precioUnitario float64) (int, error) {
	query := "INSERT INTO productos (nombre, cantidad, Precio_Unitario) VALUES (@nombre, @cantidad, @precio); SELECT CAST(SCOPE_IDENTITY() AS int)"
	var newID int
	err := db.QueryRow(query,
		sql.Named("nombre", nombre),
		sql.Named("cantidad", cantidad),
		sql.Named("precio", precioUnitario),
	).Scan(&newID)
	return newID, err
}

func ActualizarProducto(db *sql.DB, id int, nombre string, cantidad int, precioUnitario float64) error {
	query := "UPDATE productos SET nombre = @nombre, cantidad = @cantidad, Precio_Unitario = @precio WHERE id = @id"
	_, err := db.Exec(query,
		sql.Named("nombre", nombre),
		sql.Named("cantidad", cantidad),
		sql.Named("precio", precioUnitario),
		sql.Named("id", id),
	)
	return err
}

func EliminarProducto(db *sql.DB, id int) error {
	_, err := db.Exec("DELETE FROM productos WHERE id = @id", sql.Named("id", id))
	return err
}

func BuscarProductos(db *sql.DB, termino string) ([]models.Producto, error) {
	query := `
        SELECT id, nombre, cantidad, Precio_Unitario
        FROM productos
        WHERE LOWER(nombre) LIKE '%' + @termino + '%' OR CAST(id AS VARCHAR) LIKE '%' + @termino + '%'
    `
	rows, err := db.Query(query, sql.Named("termino", termino))
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var productos []models.Producto
	for rows.Next() {
		var p models.Producto
		if err := rows.Scan(&p.ID, &p.Nombre, &p.Cantidad, &p.PrecioUnitario); err != nil {
			return nil, err
		}
		productos = append(productos, p)
	}
	return productos, nil
}

//
