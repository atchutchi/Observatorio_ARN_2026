export type UserRole =
  | 'admin_arn'
  | 'analyst_arn'
  | 'operator_telecel'
  | 'operator_orange'
  | 'operator_starlink'
  | 'viewer'

export type User = {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  role_display: string
  operator: number | null
  operator_name: string | null
  operator_code: string | null
  operator_type: string | null
  phone: string
  position: string
}

export type Operator = {
  id: number
  name: string
  legal_name: string
  code: string
  operator_type: number
  operator_type_name: string
  operator_type_code: string
  license_number: string
  contact_email: string
  contact_phone: string
  brand_color: string
  is_active: boolean
  historical_names: string[]
}

export type OperatorListItem = {
  id: number
  name: string
  code: string
  operator_type_code: string
  brand_color: string
  is_active: boolean
}

export type IndicatorCategory = {
  id: number
  code: string
  name: string
  description: string
  order: number
  is_cumulative: boolean
  indicators: Indicator[]
  indicator_count?: number
}

export type Indicator = {
  id: number
  code: string
  name: string
  category: number
  category_code: string
  category_name: string
  parent: number | null
  unit: string
  level: number
  is_calculated: boolean
  formula_type: string
  order: number
  notes: string
  children: Indicator[]
}

export type Period = {
  id: number
  year: number
  quarter: number
  quarter_name: string
  month: number
  month_name: string
  start_date: string
  end_date: string
  is_locked: boolean
}

export type DataEntry = {
  id: number
  indicator: number
  operator: number
  period: number
  value: string | null
  observation: string
  source: string
  is_validated: boolean
  submitted_at: string
  updated_at: string
}

export type CumulativeData = {
  id: number
  indicator: number
  operator: number
  year: number
  cumulative_type: '3M' | '6M' | '9M' | '12M'
  value: string | null
  observation: string
  source: string
  is_validated: boolean
}

export type FileUpload = {
  id: number
  operator: number
  original_filename: string
  file_type: string
  year: number
  quarter: number | null
  status: 'uploaded' | 'processing' | 'processed' | 'error' | 'validated'
  processing_log: string
  records_imported: number
  records_errors: number
  uploaded_at: string
  processed_at: string | null
}

export type AuthTokens = {
  access: string
  refresh: string
}
