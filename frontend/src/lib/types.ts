/**
 * Shared types for the frontend
 */

export interface User {
	id: string;
	email: string;
	display_name: string;
	avatar_url?: string | null;
	role: 'user' | 'admin';
	is_active: boolean;
	is_verified: boolean;
	must_change_password: boolean;
	last_login_at?: string | null;
	created_at: string;
	updated_at: string;
}

export interface Token {
	access_token: string;
	token_type: string;
	expires_in: number;
}

export interface TokenRefresh {
	refresh_token: string;
}

export interface Category {
	id: string;
	slug: string;
	name: string;
	description?: string | null;
	icon?: string | null;
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
	validated_by_admin?: boolean;
}

export interface RecipeIngredient {
	ingredient_id: string;
	name?: string | null;
	amount: number;
	unit: string;
	notes?: string | null;
	ingredient?: Ingredient;
}

export interface Recipe {
	id: string;
	author_id: string;
	title: string;
	slug: string;
	description?: string | null;
	category_id: string;
	category?: Category;
	image_url?: string | null;
	prep_time_minutes?: number | null;
	cook_time_minutes?: number | null;
	servings?: number | null;
	difficulty?: string | null;
	instructions: string;
	ingredients: RecipeIngredient[];
	tags?: Tag[];
	is_public: boolean;
	visit_count: number;
	save_count: number;
	avg_rating: number;
	rating_count: number;
	created_at: string;
	updated_at: string;
	deleted_at?: string | null;
	author?: User;
	similar_recipes?: SimilarRecipe[];
}

export interface SimilarRecipe {
	id: string;
	slug: string;
	title: string;
	similarity: number;
}

export interface RecipeFilters {
	category?: string;
	tags?: string[];
	ingredients?: string[];
	query?: string;
	difficulty?: string;
	maxTime?: number;
	sort?: 'recent' | 'visited' | 'saved' | 'top_rated';
	page?: number;
	limit?: number;
}

export interface Rating {
	id: string;
	recipe_id: string;
	user_id: string;
	score: number;
	review_text?: string | null;
	created_at: string;
	updated_at: string;
	user?: User;
}

export interface Favorite {
	user_id: string;
	recipe_id: string;
	collection_name?: string | null;
	created_at: string;
	recipe?: Recipe;
}

export interface Visit {
	id: string;
	recipe_id: string;
	user_id?: string | null;
	visitor_fingerprint: string;
	visited_at: string;
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
	status_code?: number;
}
