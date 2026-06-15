export const validateRut = (rut: string): boolean => {
  if (!rut) return false;
  
  // Limpiar el RUT de puntos, guiones y espacios
  const cleanRut = rut.replace(/[^0-9kK]/g, '').toUpperCase();
  
  // Un RUT chileno tiene mínimo 7 caracteres (6 dígitos de cuerpo + 1 DV)
  // y máximo 9 (8 dígitos de cuerpo + 1 DV)
  if (cleanRut.length < 7 || cleanRut.length > 9) return false;
  
  const body = cleanRut.slice(0, -1);
  const dv = cleanRut.slice(-1);
  
  // Calcular dígito verificador con algoritmo Módulo 11
  let sum = 0;
  let multiplier = 2;
  
  for (let i = body.length - 1; i >= 0; i--) {
    sum += parseInt(body[i]) * multiplier;
    multiplier = multiplier === 7 ? 2 : multiplier + 1;
  }
  
  const remainder = sum % 11;
  const expectedDv = 11 - remainder;
  
  let expectedDvStr: string;
  if (expectedDv === 11) expectedDvStr = '0';
  else if (expectedDv === 10) expectedDvStr = 'K';
  else expectedDvStr = expectedDv.toString();
  
  return dv === expectedDvStr;
};

export const formatRut = (rut: string): string => {
  // Eliminar todo lo que no sea número o K
  let cleanRut = rut.replace(/[^0-9kK]/g, '').toUpperCase();
  
  if (cleanRut.length === 0) return '';
  if (cleanRut.length <= 1) return cleanRut;
  
  // Extraer cuerpo y dígito verificador
  const dv = cleanRut.slice(-1);
  const body = cleanRut.slice(0, -1);
  
  // Formatear cuerpo con puntos
  const formattedBody = body.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  
  return `${formattedBody}-${dv}`;
};
