#!/usr/bin/env python3
"""
Script para ejecutar tests del Asistente PMP de forma organizada.
Proporciona diferentes opciones de ejecución y reportes.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y maneja errores."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Comando: {' '.join(command)}")
    print()
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error en {description}: {e}")
        return False

def install_test_dependencies():
    """Instala las dependencias de testing."""
    command = [sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"]
    return run_command(command, "Instalando dependencias de testing")

def run_unit_tests():
    """Ejecuta solo los tests unitarios."""
    command = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-m", "unit",
        "-v",
        "--tb=short"
    ]
    return run_command(command, "Ejecutando tests unitarios")

def run_integration_tests():
    """Ejecuta solo los tests de integración."""
    command = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-m", "integration",
        "-v",
        "--tb=short"
    ]
    return run_command(command, "Ejecutando tests de integración")

def run_all_tests():
    """Ejecuta todos los tests."""
    command = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v",
        "--tb=short"
    ]
    return run_command(command, "Ejecutando todos los tests")

def run_tests_with_coverage():
    """Ejecuta tests con reporte de cobertura."""
    command = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
        "-v"
    ]
    return run_command(command, "Ejecutando tests con cobertura")

def run_tests_by_category(category):
    """Ejecuta tests por categoría específica."""
    command = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-m", category,
        "-v",
        "--tb=short"
    ]
    return run_command(command, f"Ejecutando tests de categoría: {category}")

def run_specific_test_file(test_file):
    """Ejecuta un archivo de test específico."""
    command = [
        sys.executable, "-m", "pytest", 
        f"tests/{test_file}",
        "-v",
        "--tb=short"
    ]
    return run_command(command, f"Ejecutando archivo de test: {test_file}")

def run_tests_parallel():
    """Ejecuta tests en paralelo."""
    command = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-n", "auto",
        "-v"
    ]
    return run_command(command, "Ejecutando tests en paralelo")

def generate_html_report():
    """Genera reporte HTML de los tests."""
    command = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "--html=reports/test_report.html",
        "--self-contained-html",
        "-v"
    ]
    return run_command(command, "Generando reporte HTML")

def run_linting():
    """Ejecuta linting del código."""
    command = [
        sys.executable, "-m", "flake8", 
        ".", 
        "--exclude=.venv,__pycache__,build,dist",
        "--max-line-length=100"
    ]
    return run_command(command, "Ejecutando linting del código")

def run_security_check():
    """Ejecuta verificación de seguridad."""
    command = [
        sys.executable, "-m", "bandit", 
        "-r", ".", 
        "-f", "json",
        "-o", "reports/security_report.json"
    ]
    return run_command(command, "Ejecutando verificación de seguridad")

def create_reports_directory():
    """Crea el directorio de reportes si no existe."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    print(f"📁 Directorio de reportes: {reports_dir.absolute()}")

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Script para ejecutar tests del Asistente PMP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python tests/run_tests.py --all                    # Ejecutar todos los tests
  python tests/run_tests.py --unit                   # Solo tests unitarios
  python tests/run_tests.py --integration            # Solo tests de integración
  python tests/run_tests.py --coverage               # Tests con cobertura
  python tests/run_tests.py --category auth          # Tests de autenticación
  python tests/run_tests.py --file test_auth.py      # Archivo específico
  python tests/run_tests.py --parallel               # Tests en paralelo
  python tests/run_tests.py --full                   # Suite completa
        """
    )
    
    parser.add_argument(
        "--install", 
        action="store_true",
        help="Instalar dependencias de testing"
    )
    parser.add_argument(
        "--all", 
        action="store_true",
        help="Ejecutar todos los tests"
    )
    parser.add_argument(
        "--unit", 
        action="store_true",
        help="Ejecutar solo tests unitarios"
    )
    parser.add_argument(
        "--integration", 
        action="store_true",
        help="Ejecutar solo tests de integración"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Ejecutar tests con reporte de cobertura"
    )
    parser.add_argument(
        "--category", 
        type=str,
        choices=["auth", "chatbot", "database", "ui"],
        help="Ejecutar tests de una categoría específica"
    )
    parser.add_argument(
        "--file", 
        type=str,
        help="Ejecutar un archivo de test específico"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true",
        help="Ejecutar tests en paralelo"
    )
    parser.add_argument(
        "--html-report", 
        action="store_true",
        help="Generar reporte HTML"
    )
    parser.add_argument(
        "--lint", 
        action="store_true",
        help="Ejecutar linting del código"
    )
    parser.add_argument(
        "--security", 
        action="store_true",
        help="Ejecutar verificación de seguridad"
    )
    parser.add_argument(
        "--full", 
        action="store_true",
        help="Ejecutar suite completa (tests + linting + seguridad)"
    )
    
    args = parser.parse_args()
    
    # Crear directorio de reportes
    create_reports_directory()
    
    success = True
    
    # Instalar dependencias si se solicita
    if args.install:
        success &= install_test_dependencies()
    
    # Ejecutar tests según los argumentos
    if args.all:
        success &= run_all_tests()
    elif args.unit:
        success &= run_unit_tests()
    elif args.integration:
        success &= run_integration_tests()
    elif args.coverage:
        success &= run_tests_with_coverage()
    elif args.category:
        success &= run_tests_by_category(args.category)
    elif args.file:
        success &= run_specific_test_file(args.file)
    elif args.parallel:
        success &= run_tests_parallel()
    elif args.html_report:
        success &= generate_html_report()
    elif args.lint:
        success &= run_linting()
    elif args.security:
        success &= run_security_check()
    elif args.full:
        print("\n🚀 Ejecutando suite completa de testing...")
        success &= install_test_dependencies()
        success &= run_all_tests()
        success &= run_tests_with_coverage()
        success &= generate_html_report()
        success &= run_linting()
        success &= run_security_check()
    else:
        # Por defecto, ejecutar todos los tests
        success &= run_all_tests()
    
    # Resumen final
    print(f"\n{'='*60}")
    if success:
        print("🎉 ¡Todos los tests completados exitosamente!")
    else:
        print("❌ Algunos tests fallaron. Revisa los errores arriba.")
    print(f"{'='*60}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 