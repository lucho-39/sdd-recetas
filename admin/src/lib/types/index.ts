/**
 * Type definitions for Recetario IA Admin Frontend
 */

export interface User {
  id: string;
  email: string;
  display_name: string;
  avatar_url?: string;
  role: 'user' | 'admin';
  is_active: boolean;
  is_verified: boolean;
  must_change_password: boolean;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
  deactivated_at?: string;
}

export interface Category {
  id: string;
  slug: string;
  name: string;
  description?: string;
  icon?: string;
  color: string;
  sort_order: number;
  is_active: boolean;
  recetas_count?: number;
}

export interface Recipe {
  id: string;
  author_id: string;
  title: string;
  slug: string;
  description?: string;
  category_id: string;
  image_url?: string;
  prep_time_minutes?: number;
  cook_time_minutes?: number;
  servings?: number;
  difficulty?: string;
  instructions: string;
  ingredients: any[];
  is_public: boolean;
  visit_count: number;
  save_count: number;
  avg_rating: number;
  rating_count: number;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
  author?: {
    id: string;
    display_name: string;
    avatar_url?: string;
  };
  category?: {
    slug: string;
    name: string;
  };
  tags?: { id: string; name: string; slug: string }[];
}

export interface Ingredient {
  id: string;
  slug: string;
  name: string;
  category: string;
  default_unit: string;
  aliases: string[];
  is_active: boolean;
  validated_by_admin: boolean;
  validated_at?: string;
  validated_by?: string;
  rejected: boolean;
  rejection_reason?: string;
  rejected_by?: string;
  rejected_at?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
  usage_count?: number;
}

export interface Tag {
  id: string;
  slug: string;
  name: string;
  usage_count: number;
  created_by?: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface DashboardMetrics {
  active_users_7d: number;
  active_users_30d: number;
  total_recipes: number;
  recipes_this_month: number;
  searches_per_day: number;
  visits_per_day: number;
  ratings_per_day: number;
  avg_rating_global: number;
}

export interface ContentMetrics {
  recipes_by_status: { public: number; private: number; deleted: number };
  recipes_by_category: Record<string, number>;
  quality: { with_rating_ge_3: number; with_rating_ge_4: number; rating_distribution: Record<number, number> };
  engagement: { top_visited: any[]; top_saved: any[]; top_rated: any[] };
}

export interface UserMetrics {
  cohort_retention: Record<string, number>;
  activation_funnel: Record<string, number>;
  churn: { inactive_30d: number; inactive_60d: number; inactive_90d: number };
  segments: { power_users: number; casual: number; readers_only: number };
}