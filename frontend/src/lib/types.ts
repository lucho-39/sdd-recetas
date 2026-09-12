/**
 * Shared types for the frontend
 */

export interface User {
	id: string;
	email: string;
	display_name: string;
	avatar_url: string | null;
	role: 'user' | 'admin';
	is_active: boolean;
	is_verified: boolean;
	must_change_password: boolean;
	last_login_at: string | null;
	created_at: string;
	updated_at: string;
}

export interface Token {
	access_token: string;
	token_type: string;
	expires_in: number;
}

export interface Category {
	id: string;
	slug: string;
	name: string;
	description: string | null;
	icon: string | null;
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

export interface Recipe {
	id: string;
	slug: string;
	title: string;
	description: string | null;
	category: Category;
	tags: Tag[];
	author: User;
	image_url: string | null;
	prep_time_minutes: number | null;
	cook_time_minutes: number | null;
	servings: number | null;
	difficulty: string | null;
	instructions: string;
	ingredients: RecipeIngredient[];
	visit_count: number;
	save_count: number;
	avg_rating: number;
	rating_count: number;
	is_public: boolean;
	created_at: string;
	updated_at: string;
}

export interface RecipeIngredient {
	ingredient_id: string;
	quantity: number;
	unit: string;
	notes?: string;
	ingredient?: {
		id: string;
		name: string;
		category: string;
		default_unit: string;
	};
}

export interface RecipeFilters {
	category?: string;
	tags?: string[];
	ingredients?: string[];
	query?: string;
	sort?: 'recent' | 'visited' | 'saved' | 'top_rated';
}

export interface RecipeListResponse {
	recipes: Recipe[];
	total: number;
	page: number;
	limit: number;
	has_more: boolean;
}

export interface SimilarRecipe {
	id: string;
	slug: string;
	title: string;
	similarity: number;
}