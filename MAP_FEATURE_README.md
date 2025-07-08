# Interactive Transit Map Feature

## Overview

The application now includes an interactive map that displays the Paris Metro and RER network with the ability to visualize calculated routes. This feature enhances the user experience by providing a visual representation of the transit system and highlighting the recommended journey path.

## Features

### 🗺️ Interactive Map
- **Zoom & Pan**: Use mouse wheel to zoom, click and drag to pan around the map
- **Real Station Coordinates**: Shows actual geographic positions of Paris metro and RER stations
- **High-Quality Base Map**: Uses OpenStreetMap tiles optimized for France

### 🚇 Transit Network Visualization
- **Line Colors**: Each metro and RER line is displayed in its official RATP color
- **Station Markers**: 
  - Blue dots for regular stations
  - Orange dots for transfer stations (multiple lines)
- **Line Labels**: Line numbers/letters are displayed along the routes

### 🛤️ Journey Highlighting
- **Route Visualization**: Selected journeys are highlighted with:
  - Thick colored lines following the actual metro lines
  - Red dashed overlay showing the recommended path
  - Clear start (🚇) and end (🏁) markers
  - Transfer points (🔄) where line changes occur

### ♿ Accessibility Information
- **Station Accessibility**: Wheelchair-accessible stations are marked in station popups
- **Journey Accessibility**: Overall trip accessibility is displayed

## How to Use

### 1. Basic Navigation
- **Search for Route**: Enter departure and arrival stations in the search fields
- **View Results**: Multiple route options appear in the left panel
- **Select Route**: Click on any route option to see it highlighted on the map

### 2. Map Controls
- **Reset View** (🔄): Returns map to default Paris view
- **Toggle Route** (👁️): Show/hide the highlighted route (appears when route is selected)
- **Toggle Legend** (📁): Show/hide the map legend
- **Help** (❓): Display this guide

### 3. Station Information
- **Click Stations**: Click any station marker to see:
  - Station name
  - Lines serving that station
  - Accessibility information

### 4. Route Analysis
- **Multiple Options**: Compare different route options
- **Time Information**: See realistic travel times including wait times
- **Transfer Details**: Visual indication of where line changes occur

## Technical Details

### Backend Endpoints
- `/station_coordinates`: Get all station coordinates and line definitions
- `/network_data`: Get complete network with station metadata
- `/line_topology/{line_id}`: Get ordered station list for a specific line
- `/station_connections/{station_name}`: Get all lines serving a station

### Frontend Components
- **TransitMap.vue**: Main map component using Leaflet.js
- **Real-time Updates**: Map updates automatically when routes are selected
- **Responsive Design**: Adapts to different screen sizes

### Data Sources
- **Station Coordinates**: Accurate GPS coordinates for 300+ stations
- **Line Topology**: Correct station ordering for all metro and RER lines
- **Official Colors**: RATP-standard colors for all lines

## Line Color Reference

### Metro Lines
- **Line 1**: Yellow (#FFCE00)
- **Line 2**: Blue (#0055C8)
- **Line 3**: Olive (#837902)
- **Line 4**: Purple (#CF009E)
- **Line 5**: Orange (#FF7E2E)
- **Line 6**: Light Green (#82DC73)
- **Line 7**: Pink (#FA9ABA)
- **Line 8**: Light Blue (#CEADD2)
- **Line 9**: Gold (#D5C900)
- **Line 10**: Brown (#8D5524)
- **Line 11**: Brown (#8D5524)
- **Line 12**: Green (#00814F)
- **Line 13**: Light Blue (#87CEEB)
- **Line 14**: Purple (#62259D)

### RER Lines
- **RER A**: Red (#E2231A)
- **RER B**: Blue (#0055C8)
- **RER C**: Orange (#F99D1C)
- **RER D**: Green (#00A88F)
- **RER E**: Purple (#C760FF)

## Benefits

### For Users
- **Visual Journey Planning**: See exactly where you're going
- **Better Understanding**: Understand transfer points and route complexity
- **Accessibility Awareness**: Know which journeys are wheelchair accessible
- **Geographic Context**: Understand the relationship between stations and Paris geography

### For Developers
- **Extensible Design**: Easy to add new features like real-time data
- **Clean API**: Well-structured endpoints for map data
- **Performance**: Efficient rendering of complex transit networks
- **Maintainable**: Modular component structure

## Future Enhancements

- **Real-time Train Positions**: Show live train locations
- **Disruption Overlay**: Display service interruptions
- **Station Facilities**: Show amenities like elevators, toilets
- **Route Alternatives**: Compare different routing algorithms
- **Mobile Optimization**: Enhanced touch controls for mobile devices

---

*This feature significantly enhances the user experience by providing visual context to journey planning, making the transit system more accessible and easier to understand.*
