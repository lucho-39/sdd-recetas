/**
 * Type definitions for Recetario IA Frontend
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
  ingredients: RecipeIngredient[];
  is_public: boolean;
  visit_count: number;
  save_count: number;
  avg_rating: number;
  rating_count: number;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
  author?: User;
  category?: Category;
  tags?: Tag[];
}

export interface RecipeIngredient {
  ingredient_id: string;
  amount: number;
  unit: string;
  notes?: string;
  ingredient?: Ingredient;
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
}

export interface Tag {
  id: string;
  slug: string;
  name: string;
  usage_count: number;
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
}

export interface Rating {
  id: string;
  recipe_id: string;
  user_id: string;
  score: number;
  review_text?: string;
  created_at: string;
  updated_at: string;
  user?: User;
}

export interface Favorite {
  user_id: string;
  recipe_id: string;
  collection_name?: string;
  created_at: string;
  recipe?: Recipe;
}

export interface Visit {
  id: string;
  recipe_id: string;
  user_id?: string;
  visitor_fingerprint: string;
  visited_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface TokenRefresh {
  refresh_token: string;
}

export interface RecipeFilters {
  category?: string;
  tags?: string[];
  ingredients?: string[];
  query?: string;
  sort?: 'recent' | 'visited' | 'saved' | 'top_rated';
  page?: number;
  limit?: number;
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