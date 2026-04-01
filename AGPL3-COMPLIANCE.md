# AGPL3 Compliance Checklist for FermTrack

## ✅ Current Compliance Status: 100% COMPLIANT

### ✅ Completed Requirements

#### 1. License Files
- [x] Root LICENSE file (AGPL-3.0)
- [x] Backend LICENSE file (AGPL-3.0)  
- [x] Frontend LICENSE file (AGPL-3.0)
- [x] NOTICE file with copyright and source availability

#### 2. Source Code Headers
- [x] Backend Python files (`app.py`, `models.py`, `auth.py`, `batches.py`, `config.py`)
- [x] Utility files (`test_api.py`, `init.py`, `serve.py`)
- [x] Frontend HTML files (`index.html`, landing page, demo)
- [x] ESP32 C++ files (`main.cpp`, `config.h`, `sensor-test.cpp`)

#### 3. Source Code Availability (Network Copyleft)
- [x] Footer in web interface with source code link
- [x] API endpoint `/api` includes license and source info
- [x] README documents source code location
- [x] Clear notice about AGPL3 network copyleft requirements

#### 4. Package Metadata
- [x] `package.json` declares AGPL-3.0 license
- [x] README includes license section
- [x] Dependencies verified as compatible

#### 5. Copyright Attribution
- [x] All files include copyright notice
- [x] Consistent copyright holder: "FermTrack Contributors"

### 🔄 Ongoing Compliance Tasks

#### When Adding New Files:
- [ ] Add appropriate AGPL3 header to new source files
- [ ] Verify new dependencies are AGPL3-compatible
- [ ] Update copyright year if needed

#### When Deploying:
- [ ] Ensure source code remains publicly accessible
- [ ] Verify footer links work correctly
- [ ] Update source code repository URL if changed

#### When Modifying:
- [ ] Keep license headers intact
- [ ] Document significant changes
- [ ] Maintain source code availability

### 📋 Quick Reference

**License Header Template for Python:**
```python
#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - [Module Description]
Copyright (C) 2026 FermTrack Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
```

**Source Code Repository:** https://github.com/yourusername/fermtrack
**License Text:** https://www.gnu.org/licenses/agpl-3.0.html

### ⚠️ Important Reminders

1. **Network Copyleft**: Users accessing FermTrack over a network MUST have access to source code
2. **Modifications**: Any modifications must also be licensed under AGPL-3.0
3. **Distribution**: Include complete license text with any distribution
4. **Commercial Use**: Allowed, but source code must remain available

---
Last Updated: April 1, 2026
Next Review: When adding new features or dependencies