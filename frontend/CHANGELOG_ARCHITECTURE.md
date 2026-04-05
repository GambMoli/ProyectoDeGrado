# Frontend Architecture Upgrade

He reestructurado este proyecto introduciendo **Material UI** y **React Router** para mejorar la arquitectura de componentes y navegación.

### Cambios realizados:
1. **React Router (Navegación):**
   - Configuré `react-router-dom` en `main.tsx` y `App.tsx`.
   - Ahora hay soporte para rutas (`/` para el chat y `/reports` para los reportes).
2. **Nuevos Componentes y Páginas:**
   - La nueva página de métricas está encapsulada en `src/pages/Reports.tsx`. 
   - El componente `Sidebar` fue adaptado para aceptar la prop `onNavigateReports` que enlaza el botón "Reportes" al router.
3. **Página de Reportes (Mock Data & Recharts):**
   - Construida totalmente con **Material UI** para mantener consistencia con los diseños de referencia.
   - Gráficos interactivos agregados mediante `Recharts`.
4. **Dependencias:**
   - Los paquetes de MUI, Recharts y Router Dom fueron inyectados en el `package.json`.

**IMPORTANTE:** Antes de levantar el proyecto de nuevo, recuerda ejecutar `npm install` para descargar las dependencias que acabo de añadir (`@mui/material`, `react-router-dom`, `recharts`, etc).
