package handlers

import (
	"database/sql"
	"inventario/models"
	"net/http"

	"github.com/gin-gonic/gin"
)

// RegistrarRutasBusqueda registra la ruta para la búsqueda de productos
func RegistrarRutasBusqueda(router *gin.Engine, db *sql.DB) {
	// Ruta para búsqueda de productos
	router.GET("/productos/buscar", func(c *gin.Context) {
		termino := c.DefaultQuery("q", "") // Si no se proporciona "q", se toma como vacío.

		if termino == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Debe proporcionar un término de búsqueda"})
			return
		}

		productos, err := BuscarProductos(db, termino)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error al realizar la búsqueda"})
			return
		}

		c.JSON(http.StatusOK, productos)
	})
}

// BuscarProductos busca productos en la base de datos por nombre
func BuscarProductos(db *sql.DB, termino string) ([]models.Producto, error) {
	query := "SELECT id, nombre, cantidad, Precio_Unitario FROM productos WHERE nombre LIKE @termino"
	rows, err := db.Query(query, sql.Named("termino", "%"+termino+"%"))
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
