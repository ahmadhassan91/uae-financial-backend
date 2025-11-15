#!/bin/bash

# Setup script for content management system
echo "🚀 Setting up Content Management System..."

# Make scripts executable
chmod +x populate_all_content_to_database.py
chmod +x run_content_population.py
chmod +x test_content_population.py

echo "✅ Scripts are now executable"

echo ""
echo "📋 Available Commands:"
echo ""
echo "1. Populate all content to database:"
echo "   python run_content_population.py"
echo ""
echo "2. Test the population:"
echo "   python test_content_population.py"
echo ""
echo "3. Test localization service:"
echo "   python test_localization_service.py"
echo ""
echo "4. View the guide:"
echo "   cat CONTENT_POPULATION_GUIDE.md"
echo ""
echo "🎯 Next Steps:"
echo "1. Run the population script"
echo "2. Access /admin in your application"
echo "3. Go to 'Localization Management'"
echo "4. Start creating translations!"
echo ""
echo "✨ Happy translating!"