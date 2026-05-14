export function setNested(obj: Record<string, any>, path: string, value: any): void {
    const keys = path.split('.');
    let current = obj;

    for (let i = 0; i < keys.length - 1; i++) {
        const key = keys[i];
        if (!(key in current) || typeof current[key] !== 'object') {
            current[key] = {};
        }
        current = current[key];
    }

    current[keys[keys.length - 1]] = value;
}

export function getNested(obj: Record<string, any>, path: string, defaultValue: any = undefined): any {
    const keys = path.split('.');
    let current: any = obj;

    for (const key of keys) {
        if (current && typeof current === 'object' && key in current) {
            current = current[key];
        } else {
            return defaultValue;
        }
    }

    return current;
}

export function deleteNested(obj: Record<string, any>, path: string): boolean {
    const keys = path.split('.');
    let current = obj;

    for (let i = 0; i < keys.length - 1; i++) {
        const key = keys[i];
        if (!(key in current) || typeof current[key] !== 'object') {
            return false;
        }
        current = current[key];
    }

    const finalKey = keys[keys.length - 1];
    if (finalKey in current) {
        delete current[finalKey];
        return true;
    }

    return false;
}

export function getAllNestedKeys(obj: Record<string, any>): string[] {
    const keys: string[] = [];

    function recurse(current: any, path: string) {
        if (Array.isArray(current) || typeof current !== 'object' || current === null) {
            keys.push(path);
            return;
        }

        for (const key in current) {
            if (Object.hasOwn(current, key)) {
                recurse(current[key], path ? `${path}.${key}` : key);
            }
        }
    }

    recurse(obj, '');
    return keys;
}
