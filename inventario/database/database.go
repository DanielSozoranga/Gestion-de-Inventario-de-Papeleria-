package database

import (
	"database/sql"
	"fmt"

	_ "github.com/denisenkom/go-mssqldb" // Driver de SQL Server
)

func ConectarBaseDeDatos() (*sql.DB, error) {
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

//
