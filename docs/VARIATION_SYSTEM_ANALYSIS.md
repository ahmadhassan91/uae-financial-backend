# Financial Clinic Question Variation System Analysis

## Current System Architecture

### 1. Core Components

#### QuestionVariation Model
- **Purpose**: Stores alternative versions of questions
- **Key Fields**:
  - `base_question_id`: Reference to original question (e.g., "fc_q1")
  - `text_en`/`text_ar`: Bilingual question text
  - `options`: JSON array of bilingual options
  - `demographic_rules`: Targeting conditions
  - `company_ids`: Specific company assignments

#### VariationSet Model
- **Purpose**: Bundles 15 question variations together
- **Key Fields**:
  - `set_type`: 'industry', 'demographic', 'language', 'custom'
  - `q1_variation_id` through `q15_variation_id`: Foreign keys to variations
  - `is_template`: Can be used as template for other sets

#### CompanyTracker Model
- **Purpose**: Links companies to variation sets
- **Key Fields**:
  - `variation_set_id`: Foreign key to assigned variation set
  - `question_variation_mapping`: Alternative mapping format

#### QuestionVariationService
- **Purpose**: Manages variation logic and validation
- **Key Methods**:
  - `create_question_variation()`: Creates new variations
  - `get_best_variation_for_profile()`: Selects best variation based on demographics
  - `validate_question_variation()`: Ensures consistency

### 2. Current Flow

1. Frontend calls `/questions/{profile_id}` with optional `company_url` parameter
2. Backend fetches base questions
3. If `company_url` provided, checks for variations
4. Applies variations based on:
   - Assigned variation set (Priority 1)
   - Individual question variations (Priority 2)
   - Demographic matching rules

### 3. Current Issues

#### Problem 1: Unintended Variation Application
- **Issue**: Variations appear even when not intended
- **Cause**: Frontend always sends `company_url` when company parameter exists
- **Impact**: Default questions replaced with variations unexpectedly

#### Problem 2: No Explicit Control
- **Issue**: No flag to explicitly enable/disable variations
- **Cause**: System assumes variations should always apply if company_url exists
- **Impact**: Cannot easily use default questions for companies with variations

#### Problem 3: Variation Management Complexity
- **Issue**: Multiple ways to assign variations (sets, individual, mapping)
- **Cause**: System evolved over time with multiple approaches
- **Impact**: Confusing to manage and debug

## Recommended Improvements

### 1. Add Explicit Variation Control

#### Add `enable_variations` flag to CompanyTracker
```python
class CompanyTracker(Base):
    # ... existing fields ...
    enable_variations = Column(Boolean, default=False, index=True)
    variations_enabled_at = Column(DateTime(timezone=True), nullable=True)
    variations_enabled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
```

#### Update API to respect the flag
```python
@router.get("/questions/{profile_id}")
async def get_financial_clinic_questions(
    profile_id: int,
    company_url: Optional[str] = None,
    force_variations: Optional[bool] = False  # Admin override
):
    # Only apply variations if explicitly enabled or forced
    if company_url and (company.enable_variations or force_variations):
        # Apply variation logic
        pass
```

### 2. Implement Variation Preview System

#### Add preview endpoint
```python
@router.get("/questions/{profile_id}/preview-variations")
async def preview_question_variations(
    profile_id: int,
    company_url: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Return both default and variation questions for comparison"""
```

### 3. Create Variation Management UI

#### Admin endpoints needed:
- `GET /admin/variations/sets` - List all variation sets
- `POST /admin/variations/sets` - Create new variation set
- `PUT /admin/companies/{id}/variations` - Assign/unassign variations
- `GET /admin/companies/{id}/variations/status` - Check variation status

### 4. Improve Variation Validation

#### Add stricter validation rules:
- Ensure variations maintain psychometric properties
- Validate bilingual content completeness
- Check scoring compatibility
- Verify demographic rule logic

### 5. Add Audit Trail

#### Track variation changes:
```python
class VariationAssignmentLog(Base):
    __tablename__ = "variation_assignment_logs"
    
    company_id = Column(Integer, ForeignKey("company_trackers.id"))
    variation_set_id = Column(Integer, ForeignKey("variation_sets.id"))
    action = Column(String(20))  # 'assigned', 'unassigned', 'enabled', 'disabled'
    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(Text, nullable=True)
```

## Implementation Steps

### Phase 1: Immediate Fix (Low Risk)
1. Add `enable_variations` flag to CompanyTracker model
2. Create migration to add the column
3. Update question fetching logic to check the flag
4. Set default to False for all existing companies

### Phase 2: Management Tools (Medium Risk)
1. Create admin endpoints for variation management
2. Build preview functionality
3. Add bulk enable/disable operations
4. Create variation assignment audit log

### Phase 3: Advanced Features (High Risk)
1. Implement A/B testing framework
2. Add variation performance analytics
3. Create variation template system
4. Implement automated variation suggestions

## Migration Scripts

### Add enable_variations column
```sql
ALTER TABLE company_trackers 
ADD COLUMN enable_variations BOOLEAN DEFAULT FALSE,
ADD COLUMN variations_enabled_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN variations_enabled_by INTEGER REFERENCES users(id);
```

### Update existing companies
```sql
-- Only enable variations for companies that explicitly have variation sets
UPDATE company_trackers 
SET enable_variations = TRUE 
WHERE variation_set_id IS NOT NULL;
```

## Testing Strategy

### 1. Unit Tests
- Test variation logic with/without enable flag
- Test demographic rule matching
- Test bilingual content handling

### 2. Integration Tests
- Test full question flow with variations enabled/disabled
- Test company URL parameter handling
- Test preview functionality

### 3. User Acceptance Tests
- Verify default questions show when variations disabled
- Verify variations apply when enabled
- Test admin management interface

## Rollback Plan

### If issues occur:
1. Set all `enable_variations` to False
2. Comment out variation logic in question endpoint
3. Deploy with default question behavior
4. Investigate and fix issues before re-enabling

## Success Metrics

1. **Zero unintended variations**: No variations appear unless explicitly enabled
2. **Clear audit trail**: All variation assignments are logged
3. **Admin productivity**: Easy to manage variations through UI
4. **User experience**: Clear indication when questions are customized
5. **System stability**: No impact on non-variation companies
