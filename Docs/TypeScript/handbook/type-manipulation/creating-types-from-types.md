# Creating Types from Types

TypeScript's type system is very powerful because it allows expressing types _in terms of other types_.

The simplest form of this idea is generics. Additionally, we have a wide variety of _type operators_ available to use.
It's also possible to express types in terms of _values_ that we already have.

By combining various type operators, we can express complex operations and values in a succinct, maintainable way.
In this section we'll cover ways to express a new type in terms of an existing type or value.

- [Generics](generics.md) - Types which take parameters
- [Keyof Type Operator](keyof-type-operator.md) - Using the `keyof` operator to create new types
- [Typeof Type Operator](typeof-type-operator.md) - Using the `typeof` operator to create new types
- [Indexed Access Types](indexed-access-types.md) - Using `Type['a']` syntax to access a subset of a type
- [Conditional Types](conditional-types.md) - Types which act like if statements in the type system
- [Mapped Types](mapped-types.md) - Creating types by mapping each property in an existing type
- [Template Literal Types](template-literal-types.md) - Mapped types which change properties via template literal strings
