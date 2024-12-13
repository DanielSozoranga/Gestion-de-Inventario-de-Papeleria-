package main

import (
	"inventario/database"
	"inventario/handlers" // Importar el nuevo archivo de busqueda
	"log"

	"github.com/gin-gonic/gin"
)

func main() {
	// Conectar a la base de datos
	db, err := database.ConectarBaseDeDatos()
	if err != nil {
		log.Fatal("Error al conectar a la base de datos:", err)
	}
	defer db.Close()

	// Configurar rutas y servidor
	router := gin.Default()
	handlers.RegistrarRutasProductos(router, db)

	// Iniciar el servidor
	router.Run(":8080")
}
