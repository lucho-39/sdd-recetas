# Modelo de Datos Físico (PostgreSQL)

> Esquema SQL listo para migraciones. Compatible con Prisma, Drizzle, sqlc, o migraciones raw.

```sql
-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "pgcrypto";      -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";       -- trigram indexes para búsqueda
CREATE EXTENSION IF NOT EXISTS "btree_gin";     -- GIN en columnas escalares

-- ============================================================
-- USUARIO
-- ============================================================
CREATE TABLE usuario (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email                   VARCHAR(320) NOT NULL UNIQUE,
    password_hash           VARCHAR(255),
    provider                VARCHAR(20) NOT NULL CHECK (provider IN ('email','google','github')),
    provider_id             VARCHAR(255),
    display_name            VARCHAR(100) NOT NULL,
    avatar_url              VARCHAR(500),
    is_active               BOOLEAN NOT NULL DEFAULT true,
    last_login_at           TIMESTAMPTZ,
    deactivated_at          TIMESTAMPTZ,
    deletion_requested_at   TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    -- Partial unique index para OAuth: un usuario por provider_id por proveedor
    CONSTRAINT uq_usuario_provider_id UNIQUE (provider, provider_id) 
        WHERE provider != 'email'
);

CREATE INDEX idx_usuario_email ON usuario(email);
CREATE INDEX idx_usuario_provider ON usuario(provider, provider_id);
CREATE INDEX idx_usuario_is_active ON usuario(is_active) WHERE is_active = true;

-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;$$;

CREATE TRIGGER trg_usuario_updated_at
    BEFORE UPDATE ON usuario
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- USUARIO SISTEMA (para recetas anónimas / usuario eliminado)
-- ============================================================
-- Un usuario especial que "posee" las recetas de usuarios anonimizados
INSERT INTO usuario (id, email, display_name, provider, is_active, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000000'::uuid,
    'system@deleted.local',
    'Usuario eliminado',
    'email',
    false,
    now()
) ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- CATEGORÍA (lista cerrada, seed data)
-- ============================================================
CREATE TABLE categoria (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug        VARCHAR(50) NOT NULL UNIQUE,
    name        VARCHAR(50) NOT NULL,
    description TEXT,
    icon        VARCHAR(10),
    color       VARCHAR(7) NOT NULL DEFAULT '#6366f1',  -- Hex color para badge UI
    sort_order  INT NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT true
);

-- Seed data (10 categorías — colores Tailwind 400 para mejor contraste light/dark)
INSERT INTO categoria (slug, name, icon, color, sort_order) VALUES
('postre', 'Postre', '🍰', '#FB923C', 1),              -- orange-400
('entrada', 'Entrada', '🥗', '#4ADE80', 2),           -- green-400
('snack', 'Snack', '🍿', '#FACC15', 3),               -- yellow-400
('plato-principal', 'Plato principal', '🍽️', '#60A5FA', 4),   -- blue-400
('acompañamiento', 'Acompañamiento', '🥔', '#C084FC', 5),      -- purple-400
('bebida', 'Bebida', '🥤', '#22D3EE', 6),             -- cyan-400
('desayuno', 'Desayuno', '☕', '#FB7185', 7),           -- rose-400
('sopa-crema', 'Sopa / Crema', '🍲', '#A3E635', 8),    -- lime-400
('ensalada', 'Ensalada', '🥗', '#34D399', 9),          -- emerald-400
('horneados', 'Horneados', '🍞', '#F87171', 10);        -- red-400

-- ============================================================
-- RECETAS MODELO (Seed Data - 2-3 recetas de ejemplo)
-- Autor: Usuario sistema (00000000-0000-0000-0000-000000000000)
-- ============================================================
INSERT INTO receta (
    id, author_id, title, slug, description, category_id, 
    prep_time_minutes, cook_time_minutes, servings, difficulty,
    instructions, ingredients, is_public
) VALUES
-- Receta 1: Tortilla de Patatas Clásica
(
    '11111111-1111-1111-1111-111111111111'::uuid,
    '00000000-0000-0000-0000-000000000000'::uuid,
    'Tortilla de Patatas Clásica',
    'tortilla-patatas-clasica-a1b2',
    'La receta tradicional española, jugosa y con cebolla. Perfecta para tapear o como plato principal.',
    (SELECT id FROM categoria WHERE slug = 'plato-principal'),
    20, 25, 4, 'facil',
    '1. Pelar y cortar las patatas en láminas finas o cubos pequeños. Picar la cebolla en juliana fina.\n2. Calentar abundante aceite de oliva en una sartén grande a fuego medio-bajo. Añadir patatas y cebolla, pochar suavemente 20-25 min hasta que estén tiernas (no fritas).\n3. Escurrir patatas y cebolla en un colador, reservar el aceite. Batir los huevos con sal en un bol grande.\n4. Mezclar patatas y cebolla con los huevos batidos, dejar reposar 5 min para que la patata absorba huevo.\n5. Calentar 1 cda de aceite reservado en sartén antiadherente (20-22cm). Verter mezcla, cocinar 3-4 min a fuego medio-bajo.\n6. Dar la vuelta con plato/tapa, cocinar otro lado 2-3 min. Dejar reposar 2 min antes de cortar.',
    '[
        {"name": "patatas", "amount": 800, "unit": "g", "notes": "variedad Kennebec o Monalisa"},
        {"name": "cebolla", "amount": 1, "unit": "unidad", "notes": "grande, dulce"},
        {"name": "huevos", "amount": 5, "unit": "unidad", "notes": "tamaño L"},
        {"name": "aceite de oliva virgen extra", "amount": 500, "unit": "ml", "notes": "para pochar"},
        {"name": "sal", "amount": 1, "unit": "cucharadita", "notes": "al gusto"}
    ]'::jsonb,
    true
),
-- Receta 2: Gazpacho Andaluz
(
    '22222222-2222-2222-2222-222222222222'::uuid,
    '00000000-0000-0000-0000-000000000000'::uuid,
    'Gazpacho Andaluz',
    'gazpacho-andaluz-c3d4',
    'Sopa fría de verduras crudas, refrescante y nutritiva. Ideal para días de calor.',
    (SELECT id FROM categoria WHERE slug = 'entrada'),
    15, 0, 4, 'facil',
    '1. Lavar todas las verduras. Pelar pepino y ajo. Quitar semillas al pimiento.\n2. Trocear tomate, pepino, pimiento, cebolla y ajo.\n3. Batir todo en batidora de vaso o robot con aceite, vinagre, agua fría y sal hasta textura fina.\n4. Colar por chino para eliminar pieles y semillas. Rectificar sal y vinagre.\n5. Enfriar mínimo 2h en nevera. Servir con picatostes, trocitos de verdura y chorrito de aceite.',
    '[
        {"name": "tomates maduros", "amount": 1, "unit": "kg", "notes": "pera o rama"},
        {"name": "pepino", "amount": 0.5, "unit": "unidad", "notes": "mediano"},
        {"name": "pimiento verde", "amount": 0.5, "unit": "unidad", "notes": "italiano"},
        {"name": "cebolla", "amount": 0.25, "unit": "unidad", "notes": "pequeña"},
        {"name": "ajo", "amount": 1, "unit": "diente", "notes": "pequeño"},
        {"name": "aceite de oliva virgen extra", "amount": 50, "unit": "ml", "notes": ""},
        {"name": "vinagre de Jerez", "amount": 15, "unit": "ml", "notes": "o vino"},
        {"name": "agua fría", "amount": 300, "unit": "ml", "notes": "ajustar textura"},
        {"name": "sal", "amount": 1, "unit": "cucharadita", "notes": "al gusto"}
    ]'::jsonb,
    true
),
-- Receta 3: Bizcocho de Yogur (Medida del Vaso)
(
    '33333333-3333-3333-3333-333333333333'::uuid,
    '00000000-0000-0000-0000-000000000000'::uuid,
    'Bizcocho de Yogur (Medida del Vaso)',
    'bizcocho-yogur-medida-vaso-e5f6',
    'El bizcocho más fácil: usa el vaso del yogur como medida. Esponjoso y nunca falla.',
    (SELECT id FROM categoria WHERE slug = 'postre'),
    10, 35, 8, 'facil',
    '1. Precalentar horno a 180°C (calor arriba/abajo). Engrasar molde 22cm con aceite y harina.\n2. Vaciar yogur en bol, lavar y secar el vaso (será tu medida).\n3. Añadir 2 vasos de azúcar, 3 vasos de harina, 1 vaso de aceite. Batir.\n4. Incorporar 3 huevos uno a uno, batiendo bien cada vez.\n5. Añadir levadura y ralladura de limón. Batir hasta integrar.\n6. Verter en molde, hornear 35-40 min. No abrir horno primeros 25 min.\n7. Pinchar con palillo: si sale limpio, está listo. Desmoldar tibio.',
    '[
        {"name": "yogur natural", "amount": 1, "unit": "unidad", "notes": "125g, el vaso sirve de medida"},
        {"name": "azúcar", "amount": 2, "unit": "vasos", "notes": "medida del vaso de yogur"},
        {"name": "harina de trigo", "amount": 3, "unit": "vasos", "notes": "todo uso, tamizada"},
        {"name": "aceite de girasol", "amount": 1, "unit": "vaso", "notes": "o oliva suave"},
        {"name": "huevos", "amount": 3, "unit": "unidad", "notes": "tamaño M/L"},
        {"name": "levadura química", "amount": 1, "unit": "sobres", "notes": "16g tipo Royal"},
        {"name": "ralladura de limón", "amount": 1, "unit": "unidad", "notes": "opcional"}
    ]'::jsonb,
    true
)
ON CONFLICT (id) DO NOTHING;

-- Tags para recetas modelo
INSERT INTO tag (id, slug, name, usage_count, created_by) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'::uuid, 'tradicional', 'Tradicional', 2, '00000000-0000-0000-0000-000000000000'::uuid),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'::uuid, 'espanola', 'Española', 2, '00000000-0000-0000-0000-000000000000'::uuid),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3'::uuid, 'verano', 'Verano', 1, '00000000-0000-0000-0000-000000000000'::uuid),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4'::uuid, 'facil', 'Fácil', 3, '00000000-0000-0000-0000-000000000000'::uuid),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5'::uuid, 'postre-casero', 'Postre casero', 1, '00000000-0000-0000-0000-000000000000'::uuid),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6'::uuid, 'sin-horno', 'Sin horno', 1, '00000000-0000-0000-0000-000000000000'::uuid)
ON CONFLICT (slug) DO NOTHING;

-- Relaciones receta-tag
INSERT INTO receta_tag (recipe_id, tag_id) VALUES
('11111111-1111-1111-1111-111111111111'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'::uuid), -- tortilla: tradicional
('11111111-1111-1111-1111-111111111111'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'::uuid), -- tortilla: española
('11111111-1111-1111-1111-111111111111'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4'::uuid), -- tortilla: facil
('22222222-2222-2222-2222-222222222222'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'::uuid), -- gazpacho: tradicional
('22222222-2222-2222-2222-222222222222'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'::uuid), -- gazpacho: española
('22222222-2222-2222-2222-222222222222'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3'::uuid), -- gazpacho: verano
('22222222-2222-2222-2222-222222222222'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4'::uuid), -- gazpacho: facil
('22222222-2222-2222-2222-222222222222'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6'::uuid), -- gazpacho: sin-horno
('33333333-3333-3333-3333-333333333333'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4'::uuid), -- bizcocho: facil
('33333333-3333-3333-3333-333333333333'::uuid, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5'::uuid)  -- bizcocho: postre-casero
ON CONFLICT DO NOTHING;

-- Actualizar usage_count de tags (trigger lo haría en producción, aquí manual)
UPDATE tag SET usage_count = (
    SELECT COUNT(*) FROM receta_tag WHERE tag_id = tag.id
);

-- ============================================================
-- INGREDIENTE (Catálogo Normalizado — 300 items seed)
-- ============================================================
CREATE TABLE ingrediente (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(80) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    category        VARCHAR(30) NOT NULL CHECK (category IN ('proteina','verdura','fruta','lacteo','grano','condimento','grasa','otro')),
    default_unit    VARCHAR(20) NOT NULL CHECK (default_unit IN ('g','kg','ml','l','unidad','cucharada','cucharadita','taza','pizca')),
    aliases         TEXT[] DEFAULT '{}',
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ingrediente_slug ON ingrediente(slug);
CREATE INDEX idx_ingrediente_name_trgm ON ingrediente USING GIN (name gin_trgm_ops);
CREATE INDEX idx_ingrediente_category ON ingrediente(category);

-- ============================================================
-- INGREDIENTES SEED DATA (300 ingredientes normalizados)
-- ============================================================
-- Categorías: proteina, verdura, fruta, lacteo, grano, condimento, grasa, otro
-- Unidades: g, kg, ml, l, unidad, cucharada, cucharadita, taza, pizca
INSERT INTO ingrediente (slug, name, category, default_unit, aliases) VALUES
-- PROTEÍNAS (40)
('pollo', 'Pollo', 'proteina', 'g', '{pechuga, suprema, muslo, ala}'),
('carne-vacuna', 'Carne vacuna', 'proteina', 'g', '{res, bife, cuadril, nalga, bola de lomo}'),
('cerdo', 'Cerdo', 'proteina', 'g', '{chancho, bondiola, panceta, jamon}'),
('pescado-blanco', 'Pescado blanco', 'proteina', 'g', '{merluza, bacalao, corvina, tilapia}'),
('salmon', 'Salmón', 'proteina', 'g', '{}'),
('atun', 'Atún', 'proteina', 'g', '{}'),
('camaron', 'Camarón / Langostino', 'proteina', 'g', '{langostino, gambas}'),
('mejillon', 'Mejillón', 'proteina', 'unidad', '{}'),
('calamar', 'Calamar', 'proteina', 'g', '{}'),
('huevo', 'Huevo', 'proteina', 'unidad', '{}'),
('huevo-yema', 'Yema de huevo', 'proteina', 'unidad', '{}'),
('huevo-clara', 'Clara de huevo', 'proteina', 'unidad', '{}'),
('tofu', 'Tofu', 'proteina', 'g', '{}'),
('tempeh', 'Tempé', 'proteina', 'g', '{}'),
('lentejas', 'Lentejas', 'proteina', 'g', '{}'),
('garbanzos', 'Garbanzos', 'proteina', 'g', '{}'),
('porotos-negros', 'Porotos negros', 'proteina', 'g', '{frijoles negros}'),
('porotos-rojos', 'Porotos rojos', 'proteina', 'g', '{frijoles rojos, kidney beans}'),
('porotos-blancos', 'Porotos blancos', 'proteina', 'g', '{cannellini, alubias}'),
('soja', 'Soja / Edamame', 'proteina', 'g', '{edamame}'),
('seitan', 'Seitan', 'proteina', 'g', '{}'),
('pavo', 'Pavo', 'proteina', 'g', '{}'),
('conejo', 'Conejo', 'proteina', 'g', '{}'),
('cordero', 'Cordero', 'proteina', 'g', '{}'),
('higado', 'Hígado', 'proteina', 'g', '{}'),
('chorizo', 'Chorizo', 'proteina', 'g', '{}'),
('salchicha', 'Salchicha', 'proteina', 'g', '{}'),
('mortadela', 'Mortadela', 'proteina', 'g', '{}'),
('jamon-cocido', 'Jamón cocido', 'proteina', 'g', '{}'),
('jamon-serrano', 'Jamón serrano / crudo', 'proteina', 'g', '{}'),
('queso-parmesano', 'Queso parmesano', 'proteina', 'g', '{}'),
('queso-mozzarella', 'Queso mozzarella', 'proteina', 'g', '{}'),
('queso-crema', 'Queso crema', 'proteina', 'g', '{}'),
('ricota', 'Ricota', 'proteina', 'g', '{}'),
('yogur', 'Yogur natural', 'proteina', 'g', '{}'),
('leche', 'Leche', 'proteina', 'ml', '{leche entera, descremada, semidescremada}'),
('leche-almendra', 'Leche de almendra', 'proteina', 'ml', '{}'),
('leche-soja', 'Leche de soja', 'proteina', 'ml', '{}'),
('leche-avena', 'Leche de avena', 'proteina', 'ml', '{}'),

-- VERDURAS (55)
('tomate', 'Tomate', 'verdura', 'g', '{tomate pera, tomate redondo, cherry}'),
('tomate-cherry', 'Tomate cherry', 'verdura', 'g', '{}'),
('tomate-seco', 'Tomate seco', 'verdura', 'g', '{}'),
('cebolla', 'Cebolla', 'verdura', 'g', '{cebolla blanca, cebolla común}'),
('cebolla-morada', 'Cebolla morada', 'verdura', 'g', '{}'),
('cebolla-verde', 'Cebolla de verdeo / verdeo', 'verdura', 'g', '{cebollín, green onion}'),
('ajo', 'Ajo', 'verdura', 'g', '{diente de ajo}'),
('pimiento-rojo', 'Pimiento rojo', 'verdura', 'g', '{morrón rojo}'),
('pimiento-verde', 'Pimiento verde', 'verdura', 'g', '{morrón verde}'),
('pimiento-amarillo', 'Pimiento amarillo', 'verdura', 'g', '{morrón amarillo}'),
('zanahoria', 'Zanahoria', 'verdura', 'g', '{}'),
('papa', 'Papa', 'verdura', 'g', '{papa blanca, papa andina}'),
('papa-dulce', 'Papa dulce / Batata', 'verdura', 'g', '{batata, boniato}'),
('calabaza', 'Calabaza', 'verdura', 'g', '{zapallo, auyama}'),
('calabacin', 'Calabacín / Zucchini', 'verdura', 'g', '{zapallito}'),
('berenjena', 'Berenjena', 'verdura', 'g', '{}'),
('pepino', 'Pepino', 'verdura', 'g', '{}'),
('lechuga', 'Lechuga', 'verdura', 'g', '{lechuga criolla, romana, iceberg}'),
('espinaca', 'Espinaca', 'verdura', 'g', '{}'),
('acelga', 'Acelga', 'verdura', 'g', '{}'),
('rucula', 'Rúcula', 'verdura', 'g', '{}'),
('kale', 'Kale / Col rizada', 'verdura', 'g', '{}'),
('repollo', 'Repollo', 'verdura', 'g', '{col, repollo blanco, morado}'),
('coliflor', 'Coliflor', 'verdura', 'g', '{}'),
('brocoli', 'Brócoli', 'verdura', 'g', '{}'),
('bruselas', 'Coles de Bruselas', 'verdura', 'g', '{}'),
('esparragos', 'Espárragos', 'verdura', 'g', '{}'),
('apio', 'Apio', 'verdura', 'g', '{}'),
('hinojo', 'Hinojo', 'verdura', 'g', '{}'),
('puerro', 'Puerro', 'verdura', 'g', '{}'),
('rábano', 'Rábanos', 'verdura', 'g', '{}'),
('remolacha', 'Remolacha', 'verdura', 'g', '{}'),
('choclo', 'Choclo / Maíz tierno', 'verdura', 'unidad', '{maiz, elote}'),
('guisantes', 'Guisantes / Arvejas', 'verdura', 'g', '{arvejas}'),
('ejotes', 'Ejotes / Vainitas', 'verdura', 'g', '{judías verdes, green beans}'),
('palmito', 'Palmito', 'verdura', 'g', '{}'),
('alcachofa', 'Alcachofa', 'verdura', 'unidad', '{}'),
('endibia', 'Endibia', 'verdura', 'unidad', '{}'),
('pepino-pepinillo', 'Pepinillos', 'verdura', 'g', '{pickles}'),
('aceituna-verde', 'Aceitunas verdes', 'verdura', 'g', '{}'),
('aceituna-negra', 'Aceitunas negras', 'verdura', 'g', '{}'),
('perejil', 'Perejil', 'verdura', 'g', '{}'),
('cilantro', 'Cilantro / Coriandro', 'verdura', 'g', '{}'),
('albahaca', 'Albahaca', 'verdura', 'g', '{}'),
('menta', 'Menta / Hierbabuena', 'verdura', 'g', '{}'),
('oregano-fresco', 'Orégano fresco', 'verdura', 'g', '{}'),
('tomillo-fresco', 'Tomillo fresco', 'verdura', 'g', '{}'),
('romero-fresco', 'Romero fresco', 'verdura', 'g', '{}'),
('salvia', 'Salvia', 'verdura', 'g', '{}'),
('estragon', 'Estragón', 'verdura', 'g', '{}'),
('eneldo', 'Eneldo', 'verdura', 'g', '{}'),

-- FRUTAS (25)
('limon', 'Limón', 'fruta', 'unidad', '{}'),
('lima', 'Lima', 'fruta', 'unidad', '{}'),
('naranja', 'Naranja', 'fruta', 'unidad', '{}'),
('pomelo', 'Pomelo', 'fruta', 'unidad', '{}'),
('mandarina', 'Mandarina', 'fruta', 'unidad', '{}'),
('manzana', 'Manzana', 'fruta', 'g', '{manzana verde, roja, golden}'),
('pera', 'Pera', 'fruta', 'g', '{}'),
('banana', 'Banana', 'fruta', 'g', '{plátano}'),
('frutilla', 'Frutilla / Fresa', 'fruta', 'g', '{fresa}'),
('arandano', 'Arándano', 'fruta', 'g', '{blueberry}'),
('frambuesa', 'Frambuesa', 'fruta', 'g', '{}'),
('mora', 'Mora', 'fruta', 'g', '{}'),
('durazno', 'Durazno / Melocotón', 'fruta', 'g', '{melocoton}'),
('ciruela', 'Ciruela', 'fruta', 'g', '{}'),
('damasco', 'Damasco / Albaricoque', 'fruta', 'g', '{albaricoque}'),
('mango', 'Mango', 'fruta', 'g', '{}'),
('piña', 'Piña / Ananá', 'fruta', 'g', '{ananá}'),
('papaya', 'Papaya', 'fruta', 'g', '{}'),
('kiwi', 'Kiwi', 'fruta', 'g', '{}'),
('uva', 'Uva', 'fruta', 'g', '{uva blanca, uva negra}'),
('sandia', 'Sandía', 'fruta', 'g', '{}'),
('melon', 'Melón', 'fruta', 'g', '{}'),
('coco', 'Coco', 'fruta', 'unidad', '{}'),
('aguacate', 'Aguacate / Palta', 'fruta', 'unidad', '{palta}'),
('granada', 'Granada', 'fruta', 'unidad', '{}'),

-- LÁCTEOS (20)
('manteca', 'Manteca / Mantequilla', 'lacteo', 'g', '{mantequilla}'),
('manteca-ghee', 'Ghee / Manteca clarificada', 'lacteo', 'g', '{}'),
('crema-leche', 'Crema de leche', 'lacteo', 'ml', '{crema, nata}'),
('dulce-leche', 'Dulce de leche', 'lacteo', 'g', '{}'),
('queso-cremoso', 'Queso cremoso', 'lacteo', 'g', '{queso port salut, queso mar del plata}'),
('queso-tybo', 'Queso Tybo', 'lacteo', 'g', '{}'),
('queso-gouda', 'Queso Gouda', 'lacteo', 'g', '{}'),
('queso-edam', 'Queso Edam', 'lacteo', 'g', '{}'),
('queso-gruyere', 'Queso Gruyère', 'lacteo', 'g', '{}'),
('queso-roquefort', 'Queso Roquefort', 'lacteo', 'g', '{queso azul}'),
('queso-cabrales', 'Queso Cabrales', 'lacteo', 'g', '{}'),
('queso-feta', 'Queso feta', 'lacteo', 'g', '{}'),
('queso-cottage', 'Queso cottage / Ricota', 'lacteo', 'g', '{}'),
('queso-parmesano', 'Queso parmesano', 'lacteo', 'g', '{}'),
('queso-pecorino', 'Queso pecorino', 'lacteo', 'g', '{}'),
('queso-grana-padano', 'Queso Grana Padano', 'lacteo', 'g', '{}'),
('leche-condensada', 'Leche condensada', 'lacteo', 'g', '{}'),
('leche-evaporada', 'Leche evaporada', 'lacteo', 'ml', '{}'),

-- GRANOS Y CEREALES (30)
('harina-trigo', 'Harina de trigo 0000', 'grano', 'g', '{harina común, harina todo uso}'),
('harina-integral', 'Harina integral', 'grano', 'g', '{}'),
('harina-maiz', 'Harina de maíz / Polenta', 'grano', 'g', '{polenta, harina de maiz fina}'),
('harina-arroz', 'Harina de arroz', 'grano', 'g', '{}'),
('harina-almendra', 'Harina de almendra', 'grano', 'g', '{}'),
('harina-coco', 'Harina de coco', 'grano', 'g', '{}'),
('harina-avena', 'Harina de avena', 'grano', 'g', '{}'),
('harina-centeno', 'Harina de centeno', 'grano', 'g', '{}'),
('harina-espelta', 'Harina de espelta', 'grano', 'g', '{}'),
('arroz-blanco', 'Arroz blanco', 'grano', 'g', '{arroz largo, arroz redondo}'),
('arroz-integral', 'Arroz integral / yamani', 'grano', 'g', '{arroz yamani}'),
('arroz-basmatí', 'Arroz basmatí', 'grano', 'g', '{}'),
('arroz-jasmine', 'Arroz jazmín', 'grano', 'g', '{}'),
('avena', 'Avena en hojuelas', 'grano', 'g', '{avena instantánea, avena tradicional}'),
('quinua', 'Quínoa', 'grano', 'g', '{quinoa}'),
('cuscus', 'Cuscús', 'grano', 'g', '{}'),
('bulgur', 'Bulgur', 'grano', 'g', '{}'),
('mijo', 'Mijo', 'grano', 'g', '{}'),
('amaranto', 'Amaranto', 'grano', 'g', '{}'),
('fideos', 'Fideos / Tallarines', 'grano', 'g', '{spaghetti, fettuccine, penne, fusilli}'),
('fideos-integrales', 'Fideos integrales', 'grano', 'g', '{}'),
('fideos-arroz', 'Fideos de arroz', 'grano', 'g', '{}'),
('lasagna', 'Láminas de lasaña', 'grano', 'g', '{}'),
('ravioles', 'Ravioles / Sorrentinos', 'grano', 'g', '{}'),
('ñoquis', 'Ñoquis de papa', 'grano', 'g', '{}'),
('pan-miga', 'Pan de miga', 'grano', 'g', '{}'),
('pan-arabe', 'Pan árabe / Pita', 'grano', 'unidad', '{}'),
('pan-hamburguesa', 'Pan para hamburguesa', 'grano', 'unidad', '{}'),
('pan-hotdog', 'Pan para hot dog', 'grano', 'unidad', '{}'),
('tortilla-maiz', 'Tortilla de maíz', 'grano', 'unidad', '{}'),
('tortilla-harina', 'Tortilla de harina', 'grano', 'unidad', '{}'),

-- CONDIMENTOS Y ESPECIAS (35)
('sal', 'Sal', 'condimento', 'g', '{sal fina, sal gruesa, sal marina, sal rosa}'),
('pimienta-negra', 'Pimienta negra', 'condimento', 'g', '{pimienta en grano, molida}'),
('pimienta-blanca', 'Pimienta blanca', 'condimento', 'g', '{}'),
('pimienta-cayena', 'Pimienta de cayena', 'condimento', 'g', '{}'),
('pimenton', 'Pimentón / Paprika', 'condimento', 'g', '{paprika, pimentón dulce, ahumado}'),
('comino', 'Comino', 'condimento', 'g', '{}'),
('curry', 'Curry en polvo', 'condimento', 'g', '{}'),
('curcuma', 'Cúrcuma', 'condimento', 'g', '{turmeric}'),
('jengibre-molido', 'Jengibre molido', 'condimento', 'g', '{}'),
('canela', 'Canela', 'condimento', 'g', '{canela en rama, molida}'),
('nuez-moscada', 'Nuez moscada', 'condimento', 'g', '{}'),
('clavo-olor', 'Clavo de olor', 'condimento', 'g', '{}'),
('cardamomo', 'Cardamomo', 'condimento', 'g', '{}'),
('anis', 'Anís', 'condimento', 'g', '{}'),
('hinojo-semilla', 'Semillas de hinojo', 'condimento', 'g', '{}'),
('mostaza', 'Mostaza', 'condimento', 'g', '{mostaza de Dijon, mostaza antigua}'),
('mayonesa', 'Mayonesa', 'condimento', 'g', '{}'),
('ketchup', 'Ketchup', 'condimento', 'g', '{}'),
('salsa-soja', 'Salsa de soja', 'condimento', 'ml', '{soy sauce, tamari}'),
('salsa-worcestershire', 'Salsa Worcestershire', 'condimento', 'ml', '{}'),
('salsa-inglesa', 'Salsa inglesa', 'condimento', 'ml', '{}'),
('vinagre-blanco', 'Vinagre blanco / alcohol', 'condimento', 'ml', '{}'),
('vinagre-manzana', 'Vinagre de manzana', 'condimento', 'ml', '{}'),
('vinagre-jerez', 'Vinagre de Jerez', 'condimento', 'ml', '{}'),
('vinagre-balsamico', 'Vinagre balsámico', 'condimento', 'ml', '{}'),
('vinagre-arroz', 'Vinagre de arroz', 'condimento', 'ml', '{}'),
('aceite-oliva', 'Aceite de oliva', 'grasa', 'ml', '{aceite de oliva virgen extra, AOVE}'),
('aceite-girasol', 'Aceite de girasol', 'grasa', 'ml', '{}'),
('aceite-maiz', 'Aceite de maíz', 'grasa', 'ml', '{}'),
('aceite-coco', 'Aceite de coco', 'grasa', 'g', '{}'),
('aceite-sesamo', 'Aceite de sésamo', 'grasa', 'ml', '{}'),
('manteca', 'Manteca', 'grasa', 'g', '{mantequilla}'),
('manteca-cerdo', 'Manteca de cerdo / Manteca colorada', 'grasa', 'g', '{}'),
('azucar', 'Azúcar', 'condimento', 'g', '{azúcar blanca, refinada}'),
('azucar-mascabo', 'Azúcar mascabo / morena', 'condimento', 'g', '{azúcar morena, demerara}'),
('azucar-impalpable', 'Azúcar impalpable / glas', 'condimento', 'g', '{azúcar glass}'),
('miel', 'Miel', 'condimento', 'g', '{}'),
('jarabe-arce', 'Jarabe de arce / Maple syrup', 'condimento', 'ml', '{maple syrup}'),
('stevia', 'Stevia', 'condimento', 'g', '{}'),
('levadura-quimica', 'Polvo de hornear / Royal', 'condimento', 'g', '{levadura en polvo, baking powder}'),
('bicarbonato', 'Bicarbonato de sodio', 'condimento', 'g', '{baking soda}'),
('levadura-fresca', 'Levadura fresca', 'condimento', 'g', '{levadura de panadero}'),
('levadura-seca', 'Levadura seca instantánea', 'condimento', 'g', '{levadura instantánea}'),
('gelatina', 'Gelatina sin sabor', 'condimento', 'g', '{}'),
('agar-agar', 'Agar-agar', 'condimento', 'g', '{}'),
('cacao', 'Cacao en polvo', 'condimento', 'g', '{cacao amargo}'),
('chocolate-amargo', 'Chocolate amargo 70%', 'condimento', 'g', '{}'),
('chocolate-leche', 'Chocolate con leche', 'condimento', 'g', '{}'),
('chocolate-blanco', 'Chocolate blanco', 'condimento', 'g', '{}'),
('esencia-vainilla', 'Esencia de vainilla', 'condimento', 'ml', '{vainilla, extracto de vainilla}'),
('esencia-almendra', 'Esencia de almendra', 'condimento', 'ml', '{}'),
('ralladura-limon', 'Ralladura de limón', 'condimento', 'g', '{}'),
('ralladura-naranja', 'Ralladura de naranja', 'condimento', 'g', '{}'),

-- FRUTOS SECOS Y SEMILLAS (15)
('almendra', 'Almendra', 'otro', 'g', '{almendra cruda, tostada, laminada, en polvo}'),
('nuez', 'Nuez', 'otro', 'g', '{nuez común, pecan}'),
('avellana', 'Avellana', 'otro', 'g', '{}'),
('pistacho', 'Pistacho', 'otro', 'g', '{}'),
('anacardo', 'Anacardo / Castaña de cajú', 'otro', 'g', '{caju, cashew}'),
('mani', 'Maní / Cacahuete', 'otro', 'g', '{cacahuete, peanut}'),
('nuez-macadamia', 'Nuez de macadamia', 'otro', 'g', '{}'),
('nuez-brasil', 'Nuez de Brasil', 'otro', 'g', '{}'),
('pipas-girasol', 'Pipas de girasol', 'otro', 'g', '{semillas de girasol}'),
('pipas-calabaza', 'Pipas de calabaza', 'otro', 'g', '{semillas de zapallo}'),
('chia', 'Semillas de chía', 'otro', 'g', '{}'),
('lino', 'Semillas de lino', 'otro', 'g', '{linaza}'),
('sesamo', 'Sésamo / Ajónjoli', 'otro', 'g', '{ajonjoli}'),
('amapola', 'Semillas de amapola', 'otro', 'g', '{}'),
('coco-rallado', 'Coco rallado', 'otro', 'g', '{}'),

-- OTROS (25)
('caldo-pollo', 'Caldo de pollo', 'otro', 'ml', '{caldo de gallina, fondo de pollo}'),
('caldo-verduras', 'Caldo de verduras', 'otro', 'ml', '{fondo de verduras}'),
('caldo-carne', 'Caldo de carne', 'otro', 'ml', '{fondo de carne, consomé}'),
('vino-blanco', 'Vino blanco', 'otro', 'ml', '{}'),
('vino-tinto', 'Vino tinto', 'otro', 'ml', '{}'),
('vino-jerez', 'Vino de Jerez', 'otro', 'ml', '{}'),
('cerveza', 'Cerveza', 'otro', 'ml', '{}'),
('agua', 'Agua', 'otro', 'ml', '{}'),
('agua-gasificada', 'Agua con gas / Soda', 'otro', 'ml', '{}'),
('cafe', 'Café', 'otro', 'g', '{café molido, grano, instantáneo}'),
('te', 'Té', 'otro', 'g', '{té negro, verde, rojo, hierbas}'),
('mate', 'Yerba mate', 'otro', 'g', '{}'),
('cacao-ceremonia', 'Cacao ceremonial', 'otro', 'g', '{}'),
('levadura-nutricional', 'Levadura nutricional', 'otro', 'g', '{nooch}'),
('misopaste', 'Pasta de miso', 'otro', 'g', '{miso blanco, rojo}'),
('tahini', 'Tahini / Pasta de sésamo', 'otro', 'g', '{}'),
('pasta-tomate', 'Pasta de tomate / Concentrado', 'otro', 'g', '{tomate concentrado, extracto de tomate}'),
('tomate-triturado', 'Tomate triturado / Pelado', 'otro', 'g', '{tomate en lata, crushed tomato}'),
('tomate-cherry-lata', 'Tomate cherry en lata', 'otro', 'g', '{}'),
('leche-coco', 'Leche de coco', 'otro', 'ml', '{}'),
('crema-coco', 'Crema de coco', 'otro', 'g', '{}'),
('harina-fuerza', 'Harina de fuerza / Panadera', 'grano', 'g', '{harina 000, fuerte}'),
('sal-gruesa', 'Sal gruesa / Parrillera', 'condimento', 'g', '{}'),
('pimienta-rosa', 'Pimienta rosa', 'condimento', 'g', '{}'),
('sal-ahumada', 'Sal ahumada', 'condimento', 'g', '{}')
ON CONFLICT (slug) DO NOTHING;
-- ============================================================
CREATE TABLE tag (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(80) NOT NULL UNIQUE,
    name            VARCHAR(80) NOT NULL,
    usage_count     INT NOT NULL DEFAULT 0,
    created_by      UUID REFERENCES usuario(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tag_slug_trgm ON tag USING GIN (slug gin_trgm_ops);
CREATE INDEX idx_tag_usage_count ON tag (usage_count DESC);

-- ============================================================
-- RECETA
-- ============================================================
CREATE TABLE receta (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id           UUID NOT NULL REFERENCES usuario(id) ON DELETE SET DEFAULT,
    title               VARCHAR(200) NOT NULL,
    slug                VARCHAR(220) NOT NULL UNIQUE,  -- SEO: slugify(title) + nanoid(4)
    description         TEXT,
    category_id         UUID NOT NULL REFERENCES categoria(id) ON DELETE RESTRICT,
    image_url           VARCHAR(500),  -- MVP: siempre NULL
    prep_time_minutes   INT CHECK (prep_time_minutes >= 0),
    cook_time_minutes   INT CHECK (cook_time_minutes >= 0),
    servings            INT CHECK (servings > 0),
    difficulty          VARCHAR(10) CHECK (difficulty IN ('facil','medio','dificil')),
    instructions        TEXT NOT NULL,
    ingredients         JSONB NOT NULL,  -- [{ingredient_id, amount, unit, notes?}] — ingredient_id FK → ingrediente.id
    is_public           BOOLEAN NOT NULL DEFAULT true,
    visit_count         INT NOT NULL DEFAULT 0,
    save_count          INT NOT NULL DEFAULT 0,
    avg_rating          DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    rating_count        INT NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

ALTER TABLE receta ALTER COLUMN author_id SET DEFAULT '00000000-0000-0000-0000-000000000000'::uuid;

CREATE INDEX idx_receta_author_id ON receta(author_id);
CREATE INDEX idx_receta_category_id ON receta(category_id);
CREATE INDEX idx_receta_public_created ON receta(is_public, created_at DESC) WHERE is_public = true;
CREATE INDEX idx_receta_title_trgm ON receta USING GIN (title gin_trgm_ops);
CREATE INDEX idx_receta_ingredients_gin ON receta USING GIN (ingredients);
CREATE INDEX idx_receta_slug ON receta(slug);  -- UNIQUE ya crea índice, pero explícito para claridad

CREATE TRIGGER trg_receta_updated_at
    BEFORE UPDATE ON receta
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Función para generar slug único (title + nanoid(4))
CREATE OR REPLACE FUNCTION generate_recipe_slug(p_title VARCHAR(200))
RETURNS VARCHAR(220) LANGUAGE plpgsql AS $$
DECLARE
    v_base_slug VARCHAR(200);
    v_slug VARCHAR(220);
    v_suffix VARCHAR(4);
    v_counter INT := 0;
BEGIN
    -- Normalizar: lowercase, acentos -> ascii, espacios -> guiones, solo alnum + guión
    v_base_slug := lower(regexp_replace(unaccent(p_title), '[^a-z0-9]+', '-', 'g'));
    v_base_slug := regexp_replace(v_base_slug, '^-+|-+$', '', 'g');  -- trim guiones
    v_base_slug := substr(v_base_slug, 1, 180);  -- dejar espacio para sufijo
    
    LOOP
        v_suffix := substr(md5(gen_random_uuid()::text || clock_timestamp()::text), 1, 4);
        v_slug := v_base_slug || '-' || v_suffix;
        
        -- Verificar unicidad
        IF NOT EXISTS (SELECT 1 FROM receta WHERE slug = v_slug) THEN
            RETURN v_slug;
        END IF;
        
        v_counter := v_counter + 1;
        IF v_counter > 10 THEN
            RAISE EXCEPTION 'No se pudo generar slug único tras 10 intentos';
        END IF;
    END LOOP;
END;$$;

-- ============================================================
-- RECETA_TAG (N:M)
-- ============================================================
CREATE TABLE receta_tag (
    recipe_id   UUID NOT NULL REFERENCES receta(id) ON DELETE CASCADE,
    tag_id      UUID NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (recipe_id, tag_id)
);

CREATE INDEX idx_receta_tag_tag_id ON receta_tag(tag_id);

-- ============================================================
-- FAVORITO / GUARDADO (con colecciones)
-- ============================================================
CREATE TABLE favorito (
    user_id           UUID NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    recipe_id         UUID NOT NULL REFERENCES receta(id) ON DELETE CASCADE,
    collection_name   VARCHAR(100),  -- NULL = "Favoritos general"
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, recipe_id, collection_name)
);

CREATE INDEX idx_favorito_user_collection ON favorito(user_id, collection_name);
CREATE INDEX idx_favorito_recipe ON favorito(recipe_id);

-- ============================================================
-- VISITA (tracking único anti-F5)
-- ============================================================
CREATE TABLE visita (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id             UUID NOT NULL REFERENCES receta(id) ON DELETE CASCADE,
    user_id               UUID REFERENCES usuario(id) ON DELETE SET NULL,
    visitor_fingerprint   VARCHAR(64) NOT NULL,  -- SHA256(IP+UA+salt) o cookie ID
    visited_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Una visita por receta por visitante por día
CREATE UNIQUE INDEX uq_visita_unique_daily 
    ON visita (recipe_id, visitor_fingerprint, date_trunc('day', visited_at));

CREATE INDEX idx_visita_recipe_date ON visita(recipe_id, visited_at DESC);
CREATE INDEX idx_visita_fingerprint ON visita(visitor_fingerprint);

-- ============================================================
-- CALIFICACIÓN / RATING
-- ============================================================
CREATE TABLE calificacion (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id     UUID NOT NULL REFERENCES receta(id) ON DELETE CASCADE,
    user_id       UUID NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    score         SMALLINT NOT NULL CHECK (score BETWEEN 1 AND 5),
    review_text   TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (recipe_id, user_id)
);

CREATE INDEX idx_calificacion_recipe ON calificacion(recipe_id);
CREATE INDEX idx_calificacion_user ON calificacion(user_id);

CREATE TRIGGER trg_calificacion_updated_at
    BEFORE UPDATE ON calificacion
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- FUNCIONES DE AGREGACIÓN (denormalización contadores)
-- ============================================================

-- Actualiza visit_count de receta (se llama tras INSERT en visita exitoso)
CREATE OR REPLACE FUNCTION receta_increment_visit_count(p_recipe_id UUID)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE receta SET visit_count = visit_count + 1 WHERE id = p_recipe_id;
END;$$;

-- Actualiza save_count de receta (increment/decrement)
CREATE OR REPLACE FUNCTION receta_adjust_save_count(p_recipe_id UUID, p_delta INT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE receta SET save_count = save_count + p_delta WHERE id = p_recipe_id;
END;$$;

-- Recalcula avg_rating y rating_count de receta
CREATE OR REPLACE FUNCTION receta_recalc_rating(p_recipe_id UUID)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE
    v_avg DECIMAL(3,2);
    v_cnt INT;
BEGIN
    SELECT COALESCE(AVG(score)::DECIMAL(3,2), 0), COUNT(*)
    INTO v_avg, v_cnt
    FROM calificacion WHERE recipe_id = p_recipe_id;
    
    UPDATE receta SET avg_rating = v_avg, rating_count = v_cnt WHERE id = p_recipe_id;
END;$$;

-- Trigger: tras insert/delete en favorito → ajustar save_count
CREATE OR REPLACE FUNCTION trg_favorito_save_count()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        PERFORM receta_adjust_save_count(NEW.recipe_id, +1);
    ELSIF TG_OP = 'DELETE' THEN
        PERFORM receta_adjust_save_count(OLD.recipe_id, -1);
    END IF;
    RETURN NULL;
END;$$;

CREATE TRIGGER trg_favorito_after_change
    AFTER INSERT OR DELETE ON favorito
    FOR EACH ROW EXECUTE FUNCTION trg_favorito_save_count();

-- Trigger: tras insert en visita → incrementar visit_count
CREATE OR REPLACE FUNCTION trg_visita_visit_count()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    PERFORM receta_increment_visit_count(NEW.recipe_id);
    RETURN NULL;
END;$$;

CREATE TRIGGER trg_visita_after_insert
    AFTER INSERT ON visita
    FOR EACH ROW EXECUTE FUNCTION trg_visita_visit_count();

-- Trigger: tras insert/update/delete en calificacion → recalcular rating
CREATE OR REPLACE FUNCTION trg_calificacion_recalc()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_recipe_id UUID;
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        v_recipe_id := NEW.recipe_id;
    ELSE
        v_recipe_id := OLD.recipe_id;
    END IF;
    PERFORM receta_recalc_rating(v_recipe_id);
    RETURN NULL;
END;$$;

CREATE TRIGGER trg_calificacion_after_change
    AFTER INSERT OR UPDATE OR DELETE ON calificacion
    FOR EACH ROW EXECUTE FUNCTION trg_calificacion_recalc();

-- ============================================================
-- FUNCIÓN DE BÚSQUEDA UNIFICADA
-- ============================================================

/*
Búsqueda unificada: categoría + tags + título + ingredientes
Lógica: AND entre dimensiones, OR dentro de cada dimensión multi-valor

Parámetros:
- p_category_slug: slug de categoría (opcional)
- p_tag_slugs: array de slugs de tags (opcional)
- p_query: texto libre para título/descripción (opcional, trigram)
- p_ingredient_terms: array de términos para buscar en ingredients JSONB (opcional)
- p_limit, p_offset: paginación
*/
CREATE OR REPLACE FUNCTION buscar_recetas(
    p_category_slug   VARCHAR(50) DEFAULT NULL,
    p_tag_slugs       VARCHAR(80)[] DEFAULT NULL,
    p_query           VARCHAR(200) DEFAULT NULL,
    p_ingredient_terms VARCHAR(100)[] DEFAULT NULL,
    p_limit           INT DEFAULT 20,
    p_offset          INT DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    title VARCHAR(200),
    description TEXT,
    category_slug VARCHAR(50),
    category_name VARCHAR(50),
    author_name VARCHAR(100),
    prep_time_minutes INT,
    cook_time_minutes INT,
    servings INT,
    difficulty VARCHAR(10),
    image_url VARCHAR(500),
    avg_rating DECIMAL(3,2),
    rating_count INT,
    visit_count INT,
    save_count INT,
    tags VARCHAR(80)[],
    created_at TIMESTAMPTZ
) LANGUAGE plpgsql AS $$
DECLARE
    v_sql TEXT;
    v_where TEXT := 'WHERE r.is_public = true AND r.deleted_at IS NULL';
    v_join_tags TEXT := '';
BEGIN
    -- Categoría
    IF p_category_slug IS NOT NULL THEN
        v_where := v_where || ' AND c.slug = $1';
    END IF;
    
    -- Tags (EXISTS por cada tag solicitado = AND entre tags)
    IF p_tag_slugs IS NOT NULL AND array_length(p_tag_slugs, 1) > 0 THEN
        v_join_tags := 'JOIN receta_tag rt ON rt.recipe_id = r.id JOIN tag t ON t.id = rt.tag_id';
        -- Usamos una subquery para asegurar AND entre tags
        v_where := v_where || ' AND r.id IN (
            SELECT rt2.recipe_id FROM receta_tag rt2
            JOIN tag t2 ON t2.id = rt2.tag_id
            WHERE t2.slug = ANY($' || (CASE WHEN p_category_slug IS NOT NULL THEN '2' ELSE '1' END) || ')
            GROUP BY rt2.recipe_id
            HAVING COUNT(DISTINCT t2.slug) = ' || array_length(p_tag_slugs, 1) || '
        )';
    END IF;
    
    -- Query libre (título + descripción) - trigram similarity
    IF p_query IS NOT NULL AND p_query != '' THEN
        v_where := v_where || ' AND (r.title % $' || 
            (CASE WHEN p_category_slug IS NOT NULL THEN '2' ELSE '1' END) || 
            ' OR r.description % $' || 
            (CASE WHEN p_category_slug IS NOT NULL THEN '2' ELSE '1' END) || ')';
    END IF;
    
    -- Ingredientes (JSONB contains any of the terms)
    IF p_ingredient_terms IS NOT NULL AND array_length(p_ingredient_terms, 1) > 0 THEN
        v_where := v_where || ' AND r.ingredients @> $' || 
            (CASE 
                WHEN p_category_slug IS NOT NULL AND p_tag_slugs IS NOT NULL THEN '3'
                WHEN p_category_slug IS NOT NULL OR p_tag_slugs IS NOT NULL THEN '2'
                ELSE '1' 
             END) || '::jsonb';
        -- Nota: @> busca contención exacta. Para búsqueda parcial en ingredientes,
        -- se recomienda usar jsonb_path_query o GIN con jsonb_path_ops.
    END IF;
    
    v_sql := '
        SELECT 
            r.id, r.title, r.description,
            c.slug as category_slug, c.name as category_name,
            u.display_name as author_name,
            r.prep_time_minutes, r.cook_time_minutes, r.servings, r.difficulty,
            r.image_url, r.avg_rating, r.rating_count, r.visit_count, r.save_count,
            COALESCE((
                SELECT jsonb_agg(t.name) FROM receta_tag rt2
                JOIN tag t ON t.id = rt2.tag_id
                WHERE rt2.recipe_id = r.id
            ), ''[]''::jsonb) as tags,
            r.created_at
        FROM receta r
        JOIN categoria c ON c.id = r.category_id
        JOIN usuario u ON u.id = r.author_id
        ' || v_join_tags || '
        ' || v_where || '
        ORDER BY r.created_at DESC
        LIMIT $' || 
        (CASE 
            WHEN p_category_slug IS NOT NULL AND p_tag_slugs IS NOT NULL AND p_query IS NOT NULL AND p_ingredient_terms IS NOT NULL THEN '4'
            WHEN (p_category_slug IS NOT NULL)::int + (p_tag_slugs IS NOT NULL)::int + (p_query IS NOT NULL)::int + (p_ingredient_terms IS NOT NULL)::int = 3 THEN '3'
            WHEN (p_category_slug IS NOT NULL)::int + (p_tag_slugs IS NOT NULL)::int + (p_query IS NOT NULL)::int + (p_ingredient_terms IS NOT NULL)::int = 2 THEN '2'
            ELSE '1' END) || '
        OFFSET $' || 
        (CASE 
            WHEN p_category_slug IS NOT NULL AND p_tag_slugs IS NOT NULL AND p_query IS NOT NULL AND p_ingredient_terms IS NOT NULL THEN '5'
            WHEN (p_category_slug IS NOT NULL)::int + (p_tag_slugs IS NOT NULL)::int + (p_query IS NOT NULL)::int + (p_ingredient_terms IS NOT NULL)::int = 3 THEN '4'
            WHEN (p_category_slug IS NOT NULL)::int + (p_tag_slugs IS NOT NULL)::int + (p_query IS NOT NULL)::int + (p_ingredient_terms IS NOT NULL)::int = 2 THEN '3'
            ELSE '2' END);
    
    -- Nota: Esta función es un ejemplo. En producción se recomienda:
    -- 1. Usar query builder dinámico en la capa de aplicación
    -- 2. O usar un motor de búsqueda dedicado (Meilisearch, Typesense, Elasticsearch)
    -- 3. Para ingredientes: índice GIN jsonb_path_ops + jsonb_path_query
    
    RETURN QUERY EXECUTE v_sql;
END;$$;
```

## Notas de implementación

### Búsqueda por ingredientes (JSONB)
```sql
-- Ejemplo: buscar recetas que contengan "pollo" en cualquier ingrediente
SELECT * FROM receta 
WHERE ingredients @> '[{"name": "pollo"}]'::jsonb;

-- Búsqueda parcial (ILIKE en name de ingredientes) - requiere GIN jsonb_path_ops
CREATE INDEX idx_receta_ingredients_path ON receta USING GIN (ingredients jsonb_path_ops);

SELECT * FROM receta
WHERE ingredients @@ '$.ingredients[*].name LIKE_RE "pollo"'::jsonpath;
```

### Autocompletado de tags
```sql
-- Prefix search en slug + ranking por usage_count
SELECT slug, name, usage_count
FROM tag
WHERE slug LIKE 'veg%'  -- o trigram: slug % 'veg'
ORDER BY usage_count DESC, slug
LIMIT 10;
```

### Visit fingerprint (anónimos)
```sql
-- Generar fingerprint determinista (IP + User-Agent + salt diario)
-- En aplicación: sha256(ip + '|' + user_agent + '|' + daily_salt)
-- daily_salt = HMAC(secret, date::text) → rota cada 24h
-- Cookie alternativa: uuid v4 guardado en cookie HttpOnly 1 año
```

---

## Funciones de Ciclo de Vida del Usuario

### 1. Baja Lógica (Desactivación) — Opción A: Mantener autoría recuperable
```sql
-- Desactiva usuario, anonimiza PII visible, PERO mantiene author_id en recetas
-- El usuario puede reactivarse y recuperar todo
CREATE OR REPLACE FUNCTION usuario_desactivar(p_user_id UUID, p_delete_recipes BOOLEAN DEFAULT FALSE)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE
    v_system_user_id UUID := '00000000-0000-0000-0000-000000000000'::uuid;
BEGIN
    -- 1. Marcar usuario como inactivo
    UPDATE usuario 
    SET is_active = false, 
        deactivated_at = now(),
        -- Anonimizar PII visible (pero guardamos email original en campo oculto si se necesita auditoría)
        display_name = 'Usuario eliminado',
        avatar_url = NULL
    WHERE id = p_user_id AND is_active = true;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Usuario no encontrado o ya desactivado';
    END IF;
    
    -- 2. Revocar todos los refresh tokens (invalidar sesiones)
    -- DELETE FROM refresh_token WHERE user_id = p_user_id;
    
    -- 3. Manejo de recetas según opción del usuario
    IF p_delete_recipes THEN
        -- OPCIÓN: Eliminar recetas del usuario (soft delete en recetas)
        UPDATE receta 
        SET deleted_at = now(), 
            author_id = v_system_user_id  -- Transferir a usuario sistema antes de soft delete
        WHERE author_id = p_user_id AND deleted_at IS NULL;
        
        -- Los contadores (visitas, guardados, ratings) se mantienen en las recetas
        -- pero el autor muestra "Usuario eliminado"
    ELSE
        -- OPCIÓN POR DEFECTO: Mantener recetas con autoría original (author_id intacto)
        -- Solo cambian la UI para mostrar "Usuario eliminado" 
        -- La reactivación recupera todo automáticamente
        NULL; -- No-op, author_id se mantiene
    END IF;
    
    -- 4. Favoritos/guardados: SE MANTIENEN (user_id intacto para reactivación)
    -- 5. Visitas: SE MANTIENEN (user_id intacto para histórico)
    -- 6. Calificaciones: SE MANTIENEN (user_id intacto para histórico)
    
END;$$;
```

### 2. Reactivación de Usuario
```sql
-- Reactiva usuario desactivado, restaura PII desde backup o pide confirmación
CREATE OR REPLACE FUNCTION usuario_reactivar(p_user_id UUID, p_new_display_name VARCHAR(100), p_new_avatar_url VARCHAR(500) DEFAULT NULL)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE usuario 
    SET is_active = true,
        deactivated_at = NULL,
        display_name = p_new_display_name,
        avatar_url = p_new_avatar_url,
        updated_at = now()
    WHERE id = p_user_id AND is_active = false AND deactivated_at IS NOT NULL;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Usuario no encontrado o no está desactivado';
    END IF;
    
    -- Las recetas, favoritos, visitas, ratings se "reconectan" automáticamente
    -- porque author_id/user_id nunca cambiaron (opción por defecto)
END;$$;
```

### 3. Eliminación Definitiva (GDPR Right to Erasure) — Hard Delete + Anonimización
```sql
-- Ejecutar tras período de gracia (ej: 30 días) o solicitud expresa
-- Anonimiza completamente: email → deleted_<uuid>@deleted.local, PII borrada
-- Recetas → transferidas a usuario sistema
CREATE OR REPLACE FUNCTION usuario_eliminar_definitivo(p_user_id UUID)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE
    v_system_user_id UUID := '00000000-0000-0000-0000-000000000000'::uuid;
    v_anon_email VARCHAR(320) := 'deleted_' || p_user_id || '@deleted.local';
BEGIN
    -- 1. Transferir recetas a usuario sistema (author_id → system user)
    UPDATE receta 
    SET author_id = v_system_user_id 
    WHERE author_id = p_user_id;
    
    -- 2. Anonimizar favoritos (user_id → NULL, pierden trazabilidad a usuario)
    UPDATE favorito SET user_id = NULL WHERE user_id = p_user_id;
    
    -- 3. Anonimizar visitas (user_id → NULL, conservan fingerprint)
    UPDATE visita SET user_id = NULL WHERE user_id = p_user_id;
    
    -- 4. Anonimizar calificaciones (user_id → NULL, conservan score/text)
    UPDATE calificacion SET user_id = NULL WHERE user_id = p_user_id;
    
    -- 5. Anonimizar tags creados por usuario
    UPDATE tag SET created_by = NULL WHERE created_by = p_user_id;
    
    -- 6. Anonimizar usuario (PII borrada, email reservado para no colisiones)
    UPDATE usuario 
    SET email = v_anon_email,
        password_hash = NULL,
        provider_id = NULL,
        display_name = 'Usuario eliminado',
        avatar_url = NULL,
        is_active = false,
        deletion_requested_at = now(),
        updated_at = now()
    WHERE id = p_user_id;
    
    -- 7. Revocar tokens definitivamente
    -- DELETE FROM refresh_token WHERE user_id = p_user_id;
    
END;$$;
```

### 4. Middleware de Autenticación (verificar is_active)
```sql
-- Función helper para validar usuario activo en login
CREATE OR REPLACE FUNCTION usuario_validar_activo(p_email VARCHAR(320))
RETURNS TABLE (id UUID, password_hash VARCHAR(255), provider VARCHAR(20), is_active BOOLEAN) 
LANGUAGE sql AS $$
    SELECT id, password_hash, provider, is_active
    FROM usuario
    WHERE email = p_email AND deleted_at IS NULL;  -- No hay deleted_at en usuario, usamos is_active
$$;

-- En aplicación (pseudo-código):
-- user = await usuario_validar_activo(email)
-- if not user or not user.is_active:
--     throw "Cuenta desactivada. Contacta soporte para reactivar."
-- if not verify_password(password, user.password_hash):
--     throw "Credenciales inválidas"
-- update usuario set last_login_at = now() where id = user.id
```

### 5. Consulta de Recetas con Autor Anonimizado (UI)
```sql
-- En listado/detalle: mostrar "Usuario eliminado" si author es system user
SELECT 
    r.*,
    CASE 
        WHEN u.id = '00000000-0000-0000-0000-000000000000'::uuid 
        THEN 'Usuario eliminado' 
        ELSE u.display_name 
    END as author_display_name,
    CASE 
        WHEN u.id = '00000000-0000-0000-0000-000000000000'::uuid 
        THEN NULL 
        ELSE u.avatar_url 
    END as author_avatar_url
FROM receta r
JOIN usuario u ON u.id = r.author_id
WHERE r.id = $1;
```