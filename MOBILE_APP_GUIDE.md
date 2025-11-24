"""
Guide for using translations in a mobile application
"""

# 📱 Mobile App Integration Guide

## Your Goal
Create a mobile app where users can:
1. Select a chapter (sutta)
2. Choose a language (Pali, English, Sinhala)
3. Read the text section by section
4. Switch between languages easily

## JSON Structure (Perfect for Apps!)

Each chapter JSON is already optimized for mobile apps:

```json
{
  "id": "dn3",
  "title": {
    "pali": "Cakkavattisuttaṃ",
    "english": "The Wheel-turning Monarch Discourse",
    "sinhala": "චක්කවත්ති සූත්‍රය"
  },
  "sections": [
    {
      "number": 1,
      "pali": "Evaṃ me sutaṃ...",
      "english": "Thus have I heard...",
      "sinhala": "මා විසින් මෙසේ අසන ලදී..."
    }
    // ... more sections
  ]
}
```

## Data Preparation Steps

### Step 1: Fix Numbering Issues

```bash
# Fix a single chapter
python fix_numbering.py Pāthikavaggapāḷi/chapters/dn3-Cakkavattisuttaṃ.json

# Fix all chapters
python fix_numbering.py Pāthikavaggapāḷi/chapters/dn*.json
```

**What this does:**
- Removes section numbers (80., 81., etc.) from translations
- Creates backup files automatically
- Keeps chapter structure intact

### Step 2: Verify Translation Quality

```bash
# Using OpenAI GPT-4 (best quality)
export OPENAI_API_KEY="your-key"
python verify_translations.py Pāthikavaggapāḷi/chapters/dn3-Cakkavattisuttaṃ.json --provider openai

# Using Anthropic Claude (also excellent)
export ANTHROPIC_API_KEY="your-key"
python verify_translations.py input.json --provider anthropic

# Using Cohere (good and affordable)
export COHERE_API_KEY="your-key"
python verify_translations.py input.json --provider cohere
```

**What this does:**
- Checks translation accuracy (scores 1-10)
- Identifies mistranslations
- Verifies Buddhist terminology
- Generates detailed report

### Step 3: Organize for Mobile App

Create a simple index file:

```bash
python -c "
import json, os

chapters = []
for file in sorted(os.listdir('Pāthikavaggapāḷi/chapters')):
    if file.endswith('.json') and file.startswith('dn'):
        with open(os.path.join('Pāthikavaggapāḷi/chapters', file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            chapters.append({
                'id': data['id'],
                'title': data['title'],
                'sections_count': len(data['sections']),
                'file': file
            })

with open('chapters_index.json', 'w', encoding='utf-8') as f:
    json.dump({'chapters': chapters}, f, ensure_ascii=False, indent=2)

print('Created chapters_index.json')
"
```

## Mobile App Implementation

### Option 1: React Native

```javascript
// Load chapter
import chapter from './data/chapters/dn3-Cakkavattisuttaṃ.json';

// Display sections
const SectionViewer = () => {
  const [language, setLanguage] = useState('english');
  
  return (
    <ScrollView>
      <Text style={styles.title}>{chapter.title[language]}</Text>
      
      {chapter.sections.map((section, index) => (
        <View key={index} style={styles.section}>
          <Text style={styles.number}>Section {section.number}</Text>
          <Text style={styles.text}>{section[language]}</Text>
        </View>
      ))}
      
      {/* Language selector */}
      <LanguageSelector onChange={setLanguage} />
    </ScrollView>
  );
};
```

### Option 2: Flutter

```dart
// Load chapter
final chapter = json.decode(
  await rootBundle.loadString('assets/chapters/dn3.json')
);

// Display sections
class SectionViewer extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    String language = 'english';
    
    return ListView.builder(
      itemCount: chapter['sections'].length,
      itemBuilder: (context, index) {
        final section = chapter['sections'][index];
        return Card(
          child: Column(
            children: [
              Text('Section ${section['number']}'),
              Text(section[language]),
            ],
          ),
        );
      },
    );
  }
}
```

### Option 3: Native Android (Kotlin)

```kotlin
data class Section(
    val number: Int,
    val pali: String,
    val english: String,
    val sinhala: String
)

data class Chapter(
    val id: String,
    val title: Map<String, String>,
    val sections: List<Section>
)

// Load and parse JSON
val jsonString = assets.open("chapters/dn3.json").bufferedReader().use { it.readText() }
val chapter = Gson().fromJson(jsonString, Chapter::class.java)

// Display in RecyclerView
adapter.submitList(chapter.sections)
```

### Option 4: Native iOS (Swift)

```swift
struct Section: Codable {
    let number: Int
    let pali: String
    let english: String
    let sinhala: String
}

struct Chapter: Codable {
    let id: String
    let title: [String: String]
    let sections: [Section]
}

// Load JSON
if let url = Bundle.main.url(forResource: "dn3", withExtension: "json"),
   let data = try? Data(contentsOf: url),
   let chapter = try? JSONDecoder().decode(Chapter.self, from: data) {
    // Display sections
    sections = chapter.sections
}
```

## App Features to Implement

### Core Features
- ✅ Chapter list with titles in all languages
- ✅ Section-by-section reading
- ✅ Language switcher (Pali/English/Sinhala)
- ✅ Smooth scrolling
- ✅ Save reading progress
- ✅ Bookmark sections

### Enhanced Features
- 📚 Search within chapters
- 🔖 Favorites/bookmarks
- 🌓 Dark/light mode
- 📏 Font size adjustment
- 🔊 Text-to-speech (for Sinhala/English)
- 📤 Share sections
- 💾 Offline mode
- 🎨 Custom themes

### Advanced Features
- 🔍 Cross-reference similar passages
- 📝 Personal notes on sections
- 🎯 Highlight important text
- 📊 Reading statistics
- 🔄 Sync across devices
- 🌐 Community translations
- 🎓 Study guides

## Sample App Architecture

```
app/
├── data/
│   ├── chapters/
│   │   ├── dn1-Pāthikasuttaṃ.json
│   │   ├── dn2-Udumbarikasuttaṃ.json
│   │   └── dn3-Cakkavattisuttaṃ.json
│   └── chapters_index.json
├── screens/
│   ├── ChapterListScreen
│   ├── ChapterDetailScreen
│   └── SettingsScreen
├── components/
│   ├── SectionCard
│   ├── LanguageSelector
│   └── SearchBar
└── utils/
    ├── JSONLoader
    ├── BookmarkManager
    └── TextFormatter
```

## Best Practices

### 1. Performance
- ✅ Load chapters lazily (on-demand)
- ✅ Cache loaded chapters in memory
- ✅ Virtualize long section lists
- ✅ Compress JSON files if needed

### 2. User Experience
- ✅ Remember user's language preference
- ✅ Save scroll position
- ✅ Smooth language switching
- ✅ Offline-first approach

### 3. Accessibility
- ✅ Support screen readers
- ✅ Adjustable font sizes
- ✅ High contrast mode
- ✅ RTL support (for future languages)

### 4. Data Management
- ✅ Bundle essential chapters with app
- ✅ Download additional chapters as needed
- ✅ Version control for translations
- ✅ Update mechanism

## API Design (If Using Backend)

```javascript
// REST API endpoints
GET /api/chapters                    // List all chapters
GET /api/chapters/:id                // Get specific chapter
GET /api/chapters/:id/sections       // Get all sections
GET /api/chapters/:id/sections/:num  // Get specific section
GET /api/search?q=dhamma             // Search across chapters

// Response format (same as JSON files)
{
  "id": "dn3",
  "title": {...},
  "sections": [...]
}
```

## Deployment Considerations

### File Size
- Each chapter JSON: 50-300 KB
- Total for 10 chapters: ~1-2 MB
- Acceptable for mobile app bundle

### Updates
- Version JSON files
- Implement diff-based updates
- Allow selective downloads

### Storage
- Option 1: Bundle all in app (simple, offline)
- Option 2: Download on demand (smaller app size)
- Option 3: Hybrid (bundle popular, download rest)

## Testing Checklist

- [ ] Load and display chapters correctly
- [ ] Switch between languages smoothly
- [ ] Handle Unicode (Pali/Sinhala) properly
- [ ] Scroll performance with long chapters
- [ ] Search functionality works
- [ ] Bookmarks persist
- [ ] Works offline
- [ ] Handles missing data gracefully

## Sample Mobile App Flow

```
1. App Launch
   ↓
2. Load chapters_index.json
   ↓
3. Display Chapter List
   ├─ Show titles in selected language
   └─ Show section counts
   ↓
4. User selects chapter
   ↓
5. Load chapter JSON
   ↓
6. Display Chapter Detail
   ├─ Show title
   ├─ Language selector
   └─ Section list
   ↓
7. User reads sections
   ├─ Scroll through sections
   ├─ Switch languages
   └─ Bookmark/highlight
   ↓
8. Save progress & preferences
```

## Recommended AI Providers for Verification

### For Best Quality (Enterprise)
1. **OpenAI GPT-4** - Best overall, most accurate
   - Cost: ~$0.03 per 1K tokens (input), $0.06 (output)
   - Best for: Final quality check

2. **Anthropic Claude 3 Opus** - Excellent for Buddhist texts
   - Cost: ~$0.015 per 1K tokens
   - Best for: Nuanced philosophical content

### For Good Quality (Cost-Effective)
3. **Cohere Command-R+** - Good balance of quality and cost
   - Cost: ~$0.003 per 1K tokens
   - Best for: Bulk verification

4. **Mistral Large** - Open-source friendly
   - Cost: ~$0.002 per 1K tokens
   - Best for: European compliance needs

### Recommendation
Start with **Cohere** for bulk verification, then use **GPT-4 or Claude** for sections that need review.

## Next Steps

1. **Fix numbering** in all chapters:
   ```bash
   python fix_numbering.py Pāthikavaggapāḷi/chapters/dn*.json
   ```

2. **Verify quality** of critical chapters:
   ```bash
   python verify_translations.py Pāthikavaggapāḷi/chapters/dn1-*.json --provider cohere
   ```

3. **Create index** for mobile app:
   ```bash
   # Use the Python snippet above
   ```

4. **Start mobile app development**:
   - Choose framework (React Native/Flutter/Native)
   - Implement chapter list
   - Implement section viewer
   - Add language switcher

5. **Test thoroughly**:
   - All chapters load
   - Unicode displays correctly
   - Performance is good

---

**Your translations are now mobile-app ready!** 📱✨

The JSON structure is perfect for apps, and with the verification tools, you can ensure high quality before releasing.

