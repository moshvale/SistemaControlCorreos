# Script para organizar archivos de distribución PDF + Markdown
# PowerShell: organizar_distribucion.ps1

param(
    [string]$OutputPath = "C:\Outlook-Sync-Distribution-Complete"
)

Write-Host "`n" -ForegroundColor White
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Organizador de Distribución" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Crear estructura de carpetas
$Folders = @(
    "$OutputPath\00-INICIO",
    "$OutputPath\01-USUARIOS",
    "$OutputPath\02-TECNICOS",
    "$OutputPath\03-DESARROLLADORES",
    "$OutputPath\04-ADMINISTRADORES",
    "$OutputPath\99-SCRIPTS"
)

Write-Host "`n📁 Creando estructura de carpetas..." -ForegroundColor Green

foreach ($folder in $Folders) {
    if ((Test-Path $folder) -eq $false) {
        New-Item -Path $folder -ItemType Directory -Force | Out-Null
        Write-Host "  ✓ $folder"
    }
}

# Copiar archivos
Write-Host "`n📄 Copiando archivos de documentación..." -ForegroundColor Green

# 00-INICIO (Punto de entrada)
Copy-Item -Path "INDICE_DOCUMENTACION.pdf" -Destination "$OutputPath\00-INICIO\" -Force
Copy-Item -Path "README.md" -Destination "$OutputPath\00-INICIO\" -ErrorAction SilentlyContinue

# 01-USUARIOS (Para usuarios finales)
Copy-Item -Path "MANUAL_COMPLETO_CLIENTE.pdf" -Destination "$OutputPath\01-USUARIOS\" -Force
Copy-Item -Path "MANUAL_COMPLETO_CLIENTE.md" -Destination "$OutputPath\01-USUARIOS\" -Force
Copy-Item -Path "QUICK_START_CLIENT.pdf" -Destination "$OutputPath\01-USUARIOS\" -Force
Copy-Item -Path "QUICK_START_CLIENT.md" -Destination "$OutputPath\01-USUARIOS\" -Force

# 02-TECNICOS (Para técnicos e instalación)
Copy-Item -Path "CLIENT_INSTALLATION.pdf" -Destination "$OutputPath\02-TECNICOS\" -Force
Copy-Item -Path "CLIENT_INSTALLATION.md" -Destination "$OutputPath\02-TECNICOS\" -Force
Copy-Item -Path "install_client.bat" -Destination "$OutputPath\02-TECNICOS\" -ErrorAction SilentlyContinue
Copy-Item -Path "outlook_sync_config.json.example" -Destination "$OutputPath\02-TECNICOS\" -ErrorAction SilentlyContinue

# 03-DESARROLLADORES (Para arquitectos y devs)
Copy-Item -Path "CLIENT_ARCHITECTURE.pdf" -Destination "$OutputPath\03-DESARROLLADORES\" -Force
Copy-Item -Path "CLIENT_ARCHITECTURE.md" -Destination "$OutputPath\03-DESARROLLADORES\" -Force
Copy-Item -Path "outlook_sync_agent.py" -Destination "$OutputPath\03-DESARROLLADORES\" -ErrorAction SilentlyContinue

# 04-ADMINISTRADORES (Para admins de TI)
Copy-Item -Path "GUIA_ADMINISTRADOR_DISTRIBUCION.pdf" -Destination "$OutputPath\04-ADMINISTRADORES\" -Force
Copy-Item -Path "GUIA_ADMINISTRADOR_DISTRIBUCION.md" -Destination "$OutputPath\04-ADMINISTRADORES\" -Force
Copy-Item -Path "run_sync_client.bat" -Destination "$OutputPath\04-ADMINISTRADORES\" -ErrorAction SilentlyContinue

# 99-SCRIPTS (Scripts de conversión y utilidades)
Copy-Item -Path "convert_to_pdf.py" -Destination "$OutputPath\99-SCRIPTS\" -ErrorAction SilentlyContinue
Copy-Item -Path "create_index_pdf.py" -Destination "$OutputPath\99-SCRIPTS\" -ErrorAction SilentlyContinue

Write-Host "  ✓ Archivos copiados exitosamente"

# Crear archivo README en raíz
$ReadmeContent = @"
# Outlook Sync Client - Suite de Documentación Completa

## Estructura de Carpetas

```
📦 Outlook-Sync-Distribution-Complete/
├── 📁 00-INICIO/
│   ├── INDICE_DOCUMENTACION.pdf         [EMPEZAR AQUI]
│   └── README.md
│
├── 📁 01-USUARIOS/
│   ├── MANUAL_COMPLETO_CLIENTE.pdf      [Para usuarios finales]
│   ├── MANUAL_COMPLETO_CLIENTE.md
│   ├── QUICK_START_CLIENT.pdf
│   └── QUICK_START_CLIENT.md
│
├── 📁 02-TECNICOS/
│   ├── CLIENT_INSTALLATION.pdf          [Para instalación técnica]
│   ├── CLIENT_INSTALLATION.md
│   ├── install_client.bat
│   └── outlook_sync_config.json.example
│
├── 📁 03-DESARROLLADORES/
│   ├── CLIENT_ARCHITECTURE.pdf          [Para desarrolladores]
│   ├── CLIENT_ARCHITECTURE.md
│   └── outlook_sync_agent.py
│
├── 📁 04-ADMINISTRADORES/
│   ├── GUIA_ADMINISTRADOR_DISTRIBUCION.pdf  [Para admins TI]
│   ├── GUIA_ADMINISTRADOR_DISTRIBUCION.md
│   ├── run_sync_client.bat
│   └── deploy_outlook_sync_to_users.ps1
│
└── 📁 99-SCRIPTS/
    ├── convert_to_pdf.py                [Scripts de utilidad]
    └── create_index_pdf.py
```

## 🚀 Cómo Empezar

### Para Usuarios Finales
1. Abre **00-INICIO/INDICE_DOCUMENTACION.pdf**
2. Navega a **01-USUARIOS/**
3. Lee **QUICK_START_CLIENT.pdf** para introducción rápida
4. Lee **MANUAL_COMPLETO_CLIENTE.pdf** para instrucciones detalladas

### Para Administradores TI
1. Abre **00-INICIO/INDICE_DOCUMENTACION.pdf**
2. Navega a **04-ADMINISTRADORES/**
3. Lee **GUIA_ADMINISTRADOR_DISTRIBUCION.pdf**
4. Usa los scripts de distribución en masa

### Para Técnicos
1. Navega a **02-TECNICOS/**
2. Lee **CLIENT_INSTALLATION.pdf**
3. Usa **install_client.bat** para instalar

### Para Desarrolladores
1. Navega a **03-DESARROLLADORES/**
2. Lee **CLIENT_ARCHITECTURE.pdf**
3. Revisa el código en outlook_sync_agent.py

## 📊 Resumen de Documentación

| Documento | Tamaño | Audiencia | Propósito |
|-----------|--------|-----------|------------|
| INDICE_DOCUMENTACION.pdf | 4 KB | Todos | Índice y guía de lectura |
| MANUAL_COMPLETO_CLIENTE.pdf | 27.7 KB | Usuarios Finales | Manual completo con FAQ y troubleshooting |
| GUIA_ADMINISTRADOR_DISTRIBUCION.pdf | 11.4 KB | Admins TI | Distribución en masa, monitoreo, soporte |
| CLIENT_INSTALLATION.pdf | 9 KB | Técnicos | Instalación técnica detallada |
| CLIENT_ARCHITECTURE.pdf | 9.8 KB | Desarrolladores | Arquitectura técnica y especificaciones |
| QUICK_START_CLIENT.pdf | 4.3 KB | Usuarios Avanzados | Guía rápida de inicio |

**Total: 65.8 KB**

## ✅ Versión

- **Versión**: 1.0
- **Fecha**: Marzo 2026
- **Estado**: Listo para Producción
- **Formatos**: PDF + Markdown (editable)

## 📞 Soporte

Para preguntas sobre la documentación o el cliente Outlook Sync:
- Consulta el **INDICE_DOCUMENTACION.pdf**
- Revisa la sección Troubleshooting en **MANUAL_COMPLETO_CLIENTE.pdf**
- Contacta a tu administrador de TI

---
**Suite Completa de Documentación - Outlook Sync Client v1.0**
"@

$ReadmeContent | Out-File -FilePath "$OutputPath\README.txt" -Encoding UTF8
Write-Host "  ✓ README.txt creado en raíz"

# Resumen final
Write-Host "`n" -ForegroundColor White
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "RESUMEN DE DISTRIBUCIÓN" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

$TotalSize = (Get-ChildItem -Path $OutputPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "`n📦 Carpeta de distribución creada:" -ForegroundColor Green
Write-Host "   $OutputPath" -ForegroundColor Yellow
Write-Host "`n📊 Estructura:" -ForegroundColor Green
Get-ChildItem -Path $OutputPath -Directory | ForEach-Object {
    $FileCount = (Get-ChildItem -Path $_.FullName -Recurse -File).Count
    Write-Host "   ✓ $($_.Name) ($FileCount archivos)" -ForegroundColor Cyan
}

Write-Host "`n💾 Tamaño total: $([math]::Round($TotalSize, 2)) MB" -ForegroundColor Green
Write-Host "`n✅ Distribución lista para empaquetar y distribuir" -ForegroundColor Green
Write-Host "`n"
