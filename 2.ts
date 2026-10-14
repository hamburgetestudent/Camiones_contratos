/**
 * Taller de Programación Avanzada · Unidad 2.1
 * Ejercicio 2: el programa termina, pero uno de los resultados es incorrecto.
 * Ejecuta este archivo con: node ejercicio_2_carrito.ts
 * Investiga la causa antes de modificar el código.
 */

type LineaCarrito = {
  articulo: string;
  precioUnitario: number;
  cantidad: number;
};

type ResumenCompra = {
  subtotal: number;
  envio: number;
  total: number;
};

const COSTO_ENVIO = 3500;
const ENVIO_GRATIS_DESDE = 40000;

function calcularCompra(lineas: LineaCarrito[]): ResumenCompra {
  const subtotal = lineas.reduce(
    (acumulado, linea) => acumulado + (linea.precioUnitario* linea.cantidad),
    0,
  );

  const envio = subtotal >= ENVIO_GRATIS_DESDE ? 0 : COSTO_ENVIO;
  return { subtotal, envio, total: subtotal + envio };
}

const casos: {
  nombre: string;
  lineas: LineaCarrito[];
  esperado: ResumenCompra;
}[] = [
  {
    nombre: "Compra de un artículo",
    lineas: [{ articulo: "Cable USB", precioUnitario: 7000, cantidad: 1 }],
    esperado: { subtotal: 7000, envio: 3500, total: 10500 },
  },
  {
    nombre: "Compra con varias unidades",
    lineas: [
      { articulo: "Cuaderno", precioUnitario: 5500, cantidad: 3 },
      { articulo: "Audífonos", precioUnitario: 27000, cantidad: 1 },
    ],
    esperado: { subtotal: 43500, envio: 0, total: 43500 },
  },
];

for (const caso of casos) {
  const obtenido = calcularCompra(caso.lineas);
  const coincide =
    obtenido.subtotal === caso.esperado.subtotal &&
    obtenido.envio === caso.esperado.envio &&
    obtenido.total === caso.esperado.total;

  console.log(`\n${caso.nombre}: ${coincide ? "CORRECTO" : "REVISAR"}`);
  console.log("Esperado:", caso.esperado);
  console.log("Obtenido:", obtenido);

  if (!coincide) process.exitCode = 1;
}
