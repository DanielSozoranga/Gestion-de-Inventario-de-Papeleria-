package models

type Producto struct {
	ID             int     `json:"id"`
	Nombre         string  `json:"nombre"`
	Cantidad       int     `json:"cantidad"`
	PrecioUnitario float64 `json:"Precio_Unitario"`
}

//
