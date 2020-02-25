declare module "gl-matrix" {

// prettier-ignore
export type mat2 =
  | [number, number, 
     number, number]
  | Float32Array;

// prettier-ignore
export type mat2d =
  | [number, number, 
     number, number, 
     number, number]
  | Float32Array;

// prettier-ignore
export type mat3 =
  | [number, number, number, 
     number, number, number, 
     number, number, number]
  | Float32Array;

// prettier-ignore
export type mat4 =
  | [number, number, number, number,
     number, number, number, number,
     number, number, number, number,
     number, number, number, number]
  | Float32Array;

export type quat = [number, number, number, number] | Float32Array;

// prettier-ignore
export type quat2 =
  | [number, number, number, number, 
    number, number, number, number]
  | Float32Array;

export type vec2 = [number, number] | Float32Array;
export type vec3 = [number, number, number] | Float32Array;
export type vec4 = [number, number, number, number] | Float32Array;

export module glMatrix {
    /**
     * Sets the type of array used when creating new vectors and matrices
     *
     * @param {Type} type Array type, such as Float32Array or Array
     */
    export function setMatrixArrayType(type: any): void;
    /**
     * Convert Degree To Radian
     *
     * @param {Number} a Angle in Degrees
     */
    export function toRadian(a: number): number;
    /**
     * Tests whether or not the arguments have approximately the same value, within an absolute
     * or relative tolerance of glMatrix.EPSILON (an absolute tolerance is used for values less
     * than or equal to 1.0, and a relative tolerance is used for larger values)
     *
     * @param {Number} a The first number to test.
     * @param {Number} b The second number to test.
     * @returns {Boolean} True if the numbers are approximately equal, false otherwise.
     */
    export function equals(a: number, b: number): boolean;
    /**
     * Common utilities
     * @module glMatrix
     */
    export const EPSILON: 0.000001;
    export let ARRAY_TYPE: ArrayConstructor | Float32ArrayConstructor;
    export const RANDOM: () => number;
}
export module mat2 {
    /**
     * 2x2 Matrix
     * @module mat2
     */
    /**
     * Creates a new identity mat2
     *
     * @returns {mat2} a new 2x2 matrix
     */
    export function create(): mat2;
    /**
     * Creates a new mat2 initialized with values from an existing matrix
     *
     * @param {mat2} a matrix to clone
     * @returns {mat2} a new 2x2 matrix
     */
    export function clone(a: mat2): mat2;
    /**
     * Copy the values from one mat2 to another
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the source matrix
     * @returns {mat2} out
     */
    export function copy(out: mat2, a: mat2): mat2;
    /**
     * Set a mat2 to the identity matrix
     *
     * @param {mat2} out the receiving matrix
     * @returns {mat2} out
     */
    export function identity(out: mat2): mat2;
    /**
     * Create a new mat2 with the given values
     *
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m10 Component in column 1, row 0 position (index 2)
     * @param {Number} m11 Component in column 1, row 1 position (index 3)
     * @returns {mat2} out A new 2x2 matrix
     */
    export function fromValues(m00: number, m01: number, m10: number, m11: number): mat2;
    /**
     * Set the components of a mat2 to the given values
     *
     * @param {mat2} out the receiving matrix
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m10 Component in column 1, row 0 position (index 2)
     * @param {Number} m11 Component in column 1, row 1 position (index 3)
     * @returns {mat2} out
     */
    export function set(out: mat2, m00: number, m01: number, m10: number, m11: number): mat2;
    /**
     * Transpose the values of a mat2
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the source matrix
     * @returns {mat2} out
     */
    export function transpose(out: mat2, a: mat2): mat2;
    /**
     * Inverts a mat2
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the source matrix
     * @returns {mat2} out
     */
    export function invert(out: mat2, a: mat2): mat2;
    /**
     * Calculates the adjugate of a mat2
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the source matrix
     * @returns {mat2} out
     */
    export function adjoint(out: mat2, a: mat2): mat2;
    /**
     * Calculates the determinant of a mat2
     *
     * @param {mat2} a the source matrix
     * @returns {Number} determinant of a
     */
    export function determinant(a: mat2): number;
    /**
     * Multiplies two mat2's
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the first operand
     * @param {mat2} b the second operand
     * @returns {mat2} out
     */
    export function multiply(out: mat2, a: mat2, b: mat2): mat2;
    /**
     * Rotates a mat2 by the given angle
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat2} out
     */
    export function rotate(out: mat2, a: mat2, rad: number): mat2;
    /**
     * Scales the mat2 by the dimensions in the given vec2
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the matrix to rotate
     * @param {vec2} v the vec2 to scale the matrix by
     * @returns {mat2} out
     **/
    export function scale(out: mat2, a: mat2, v: vec2): mat2;
    /**
     * Creates a matrix from a given angle
     * This is equivalent to (but much faster than):
     *
     *     mat2.identity(dest);
     *     mat2.rotate(dest, dest, rad);
     *
     * @param {mat2} out mat2 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat2} out
     */
    export function fromRotation(out: mat2, rad: number): mat2;
    /**
     * Creates a matrix from a vector scaling
     * This is equivalent to (but much faster than):
     *
     *     mat2.identity(dest);
     *     mat2.scale(dest, dest, vec);
     *
     * @param {mat2} out mat2 receiving operation result
     * @param {vec2} v Scaling vector
     * @returns {mat2} out
     */
    export function fromScaling(out: mat2, v: vec2): mat2;
    /**
     * Returns a string representation of a mat2
     *
     * @param {mat2} a matrix to represent as a string
     * @returns {String} string representation of the matrix
     */
    export function str(a: mat2): string;
    /**
     * Returns Frobenius norm of a mat2
     *
     * @param {mat2} a the matrix to calculate Frobenius norm of
     * @returns {Number} Frobenius norm
     */
    export function frob(a: mat2): number;
    /**
     * Returns L, D and U matrices (Lower triangular, Diagonal and Upper triangular) by factorizing the input matrix
     * @param {mat2} L the lower triangular matrix
     * @param {mat2} D the diagonal matrix
     * @param {mat2} U the upper triangular matrix
     * @param {mat2} a the input matrix to factorize
     */
    export function LDU(L: mat2, D: mat2, U: mat2, a: mat2): mat2[];
    /**
     * Adds two mat2's
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the first operand
     * @param {mat2} b the second operand
     * @returns {mat2} out
     */
    export function add(out: mat2, a: mat2, b: mat2): mat2;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the first operand
     * @param {mat2} b the second operand
     * @returns {mat2} out
     */
    export function subtract(out: mat2, a: mat2, b: mat2): mat2;
    /**
     * Returns whether or not the matrices have exactly the same elements in the same position (when compared with ===)
     *
     * @param {mat2} a The first matrix.
     * @param {mat2} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    export function exactEquals(a: mat2, b: mat2): boolean;
    /**
     * Returns whether or not the matrices have approximately the same elements in the same position.
     *
     * @param {mat2} a The first matrix.
     * @param {mat2} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    export function equals(a: mat2, b: mat2): boolean;
    /**
     * Multiply each element of the matrix by a scalar.
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the matrix to scale
     * @param {Number} b amount to scale the matrix's elements by
     * @returns {mat2} out
     */
    export function multiplyScalar(out: mat2, a: mat2, b: number): mat2;
    /**
     * Adds two mat2's after multiplying each element of the second operand by a scalar value.
     *
     * @param {mat2} out the receiving vector
     * @param {mat2} a the first operand
     * @param {mat2} b the second operand
     * @param {Number} scale the amount to scale b's elements by before adding
     * @returns {mat2} out
     */
    export function multiplyScalarAndAdd(out: mat2, a: mat2, b: mat2, scale: number): mat2;
    /**
     * Multiplies two mat2's
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the first operand
     * @param {mat2} b the second operand
     * @returns {mat2} out
     */
    export function mul(out: mat2, a: mat2, b: mat2): mat2;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat2} out the receiving matrix
     * @param {mat2} a the first operand
     * @param {mat2} b the second operand
     * @returns {mat2} out
     */
    export function sub(out: mat2, a: mat2, b: mat2): mat2;
}
export module mat2d {
    /**
     * 2x3 Matrix
     * @module mat2d
     * @description
     * A mat2d contains six elements defined as:
     * <pre>
     * [a, b,
     *  c, d,
     *  tx, ty]
     * </pre>
     * This is a short form for the 3x3 matrix:
     * <pre>
     * [a, b, 0,
     *  c, d, 0,
     *  tx, ty, 1]
     * </pre>
     * The last column is ignored so the array is shorter and operations are faster.
     */
    /**
     * Creates a new identity mat2d
     *
     * @returns {mat2d} a new 2x3 matrix
     */
    export function create(): mat2d;
    /**
     * Creates a new mat2d initialized with values from an existing matrix
     *
     * @param {mat2d} a matrix to clone
     * @returns {mat2d} a new 2x3 matrix
     */
    export function clone(a: mat2d): mat2d;
    /**
     * Copy the values from one mat2d to another
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the source matrix
     * @returns {mat2d} out
     */
    export function copy(out: mat2d, a: mat2d): mat2d;
    /**
     * Set a mat2d to the identity matrix
     *
     * @param {mat2d} out the receiving matrix
     * @returns {mat2d} out
     */
    export function identity(out: mat2d): mat2d;
    /**
     * Create a new mat2d with the given values
     *
     * @param {Number} a Component A (index 0)
     * @param {Number} b Component B (index 1)
     * @param {Number} c Component C (index 2)
     * @param {Number} d Component D (index 3)
     * @param {Number} tx Component TX (index 4)
     * @param {Number} ty Component TY (index 5)
     * @returns {mat2d} A new mat2d
     */
    export function fromValues(a: number, b: number, c: number, d: number, tx: number, ty: number): mat2d;
    /**
     * Set the components of a mat2d to the given values
     *
     * @param {mat2d} out the receiving matrix
     * @param {Number} a Component A (index 0)
     * @param {Number} b Component B (index 1)
     * @param {Number} c Component C (index 2)
     * @param {Number} d Component D (index 3)
     * @param {Number} tx Component TX (index 4)
     * @param {Number} ty Component TY (index 5)
     * @returns {mat2d} out
     */
    export function set(out: mat2d, a: number, b: number, c: number, d: number, tx: number, ty: number): mat2d;
    /**
     * Inverts a mat2d
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the source matrix
     * @returns {mat2d} out
     */
    export function invert(out: mat2d, a: mat2d): mat2d;
    /**
     * Calculates the determinant of a mat2d
     *
     * @param {mat2d} a the source matrix
     * @returns {Number} determinant of a
     */
    export function determinant(a: mat2d): number;
    /**
     * Multiplies two mat2d's
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the first operand
     * @param {mat2d} b the second operand
     * @returns {mat2d} out
     */
    export function multiply(out: mat2d, a: mat2d, b: mat2d): mat2d;
    /**
     * Rotates a mat2d by the given angle
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat2d} out
     */
    export function rotate(out: mat2d, a: mat2d, rad: number): mat2d;
    /**
     * Scales the mat2d by the dimensions in the given vec2
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the matrix to translate
     * @param {vec2} v the vec2 to scale the matrix by
     * @returns {mat2d} out
     **/
    export function scale(out: mat2d, a: mat2d, v: vec2): mat2d;
    /**
     * Translates the mat2d by the dimensions in the given vec2
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the matrix to translate
     * @param {vec2} v the vec2 to translate the matrix by
     * @returns {mat2d} out
     **/
    export function translate(out: mat2d, a: mat2d, v: vec2): mat2d;
    /**
     * Creates a matrix from a given angle
     * This is equivalent to (but much faster than):
     *
     *     mat2d.identity(dest);
     *     mat2d.rotate(dest, dest, rad);
     *
     * @param {mat2d} out mat2d receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat2d} out
     */
    export function fromRotation(out: mat2d, rad: number): mat2d;
    /**
     * Creates a matrix from a vector scaling
     * This is equivalent to (but much faster than):
     *
     *     mat2d.identity(dest);
     *     mat2d.scale(dest, dest, vec);
     *
     * @param {mat2d} out mat2d receiving operation result
     * @param {vec2} v Scaling vector
     * @returns {mat2d} out
     */
    export function fromScaling(out: mat2d, v: vec2): mat2d;
    /**
     * Creates a matrix from a vector translation
     * This is equivalent to (but much faster than):
     *
     *     mat2d.identity(dest);
     *     mat2d.translate(dest, dest, vec);
     *
     * @param {mat2d} out mat2d receiving operation result
     * @param {vec2} v Translation vector
     * @returns {mat2d} out
     */
    export function fromTranslation(out: mat2d, v: vec2): mat2d;
    /**
     * Returns a string representation of a mat2d
     *
     * @param {mat2d} a matrix to represent as a string
     * @returns {String} string representation of the matrix
     */
    export function str(a: mat2d): string;
    /**
     * Returns Frobenius norm of a mat2d
     *
     * @param {mat2d} a the matrix to calculate Frobenius norm of
     * @returns {Number} Frobenius norm
     */
    export function frob(a: mat2d): number;
    /**
     * Adds two mat2d's
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the first operand
     * @param {mat2d} b the second operand
     * @returns {mat2d} out
     */
    export function add(out: mat2d, a: mat2d, b: mat2d): mat2d;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the first operand
     * @param {mat2d} b the second operand
     * @returns {mat2d} out
     */
    export function subtract(out: mat2d, a: mat2d, b: mat2d): mat2d;
    /**
     * Multiply each element of the matrix by a scalar.
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the matrix to scale
     * @param {Number} b amount to scale the matrix's elements by
     * @returns {mat2d} out
     */
    export function multiplyScalar(out: mat2d, a: mat2d, b: number): mat2d;
    /**
     * Adds two mat2d's after multiplying each element of the second operand by a scalar value.
     *
     * @param {mat2d} out the receiving vector
     * @param {mat2d} a the first operand
     * @param {mat2d} b the second operand
     * @param {Number} scale the amount to scale b's elements by before adding
     * @returns {mat2d} out
     */
    export function multiplyScalarAndAdd(out: mat2d, a: mat2d, b: mat2d, scale: number): mat2d;
    /**
     * Returns whether or not the matrices have exactly the same elements in the same position (when compared with ===)
     *
     * @param {mat2d} a The first matrix.
     * @param {mat2d} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    export function exactEquals(a: mat2d, b: mat2d): boolean;
    /**
     * Returns whether or not the matrices have approximately the same elements in the same position.
     *
     * @param {mat2d} a The first matrix.
     * @param {mat2d} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    export function equals(a: mat2d, b: mat2d): boolean;
    /**
     * Multiplies two mat2d's
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the first operand
     * @param {mat2d} b the second operand
     * @returns {mat2d} out
     */
    export function mul(out: mat2d, a: mat2d, b: mat2d): mat2d;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat2d} out the receiving matrix
     * @param {mat2d} a the first operand
     * @param {mat2d} b the second operand
     * @returns {mat2d} out
     */
    export function sub(out: mat2d, a: mat2d, b: mat2d): mat2d;
}
export module mat3 {
    /**
     * 3x3 Matrix
     * @module mat3
     */
    /**
     * Creates a new identity mat3
     *
     * @returns {mat3} a new 3x3 matrix
     */
    export function create(): mat3;
    /**
     * Copies the upper-left 3x3 values into the given mat3.
     *
     * @param {mat3} out the receiving 3x3 matrix
     * @param {mat4} a   the source 4x4 matrix
     * @returns {mat3} out
     */
    export function fromMat4(out: mat3, a: mat4): mat3;
    /**
     * Creates a new mat3 initialized with values from an existing matrix
     *
     * @param {mat3} a matrix to clone
     * @returns {mat3} a new 3x3 matrix
     */
    export function clone(a: mat3): mat3;
    /**
     * Copy the values from one mat3 to another
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the source matrix
     * @returns {mat3} out
     */
    export function copy(out: mat3, a: mat3): mat3;
    /**
     * Create a new mat3 with the given values
     *
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m02 Component in column 0, row 2 position (index 2)
     * @param {Number} m10 Component in column 1, row 0 position (index 3)
     * @param {Number} m11 Component in column 1, row 1 position (index 4)
     * @param {Number} m12 Component in column 1, row 2 position (index 5)
     * @param {Number} m20 Component in column 2, row 0 position (index 6)
     * @param {Number} m21 Component in column 2, row 1 position (index 7)
     * @param {Number} m22 Component in column 2, row 2 position (index 8)
     * @returns {mat3} A new mat3
     */
    export function fromValues(m00: number, m01: number, m02: number, m10: number, m11: number, m12: number, m20: number, m21: number, m22: number): mat3;
    /**
     * Set the components of a mat3 to the given values
     *
     * @param {mat3} out the receiving matrix
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m02 Component in column 0, row 2 position (index 2)
     * @param {Number} m10 Component in column 1, row 0 position (index 3)
     * @param {Number} m11 Component in column 1, row 1 position (index 4)
     * @param {Number} m12 Component in column 1, row 2 position (index 5)
     * @param {Number} m20 Component in column 2, row 0 position (index 6)
     * @param {Number} m21 Component in column 2, row 1 position (index 7)
     * @param {Number} m22 Component in column 2, row 2 position (index 8)
     * @returns {mat3} out
     */
    export function set(out: mat3, m00: number, m01: number, m02: number, m10: number, m11: number, m12: number, m20: number, m21: number, m22: number): mat3;
    /**
     * Set a mat3 to the identity matrix
     *
     * @param {mat3} out the receiving matrix
     * @returns {mat3} out
     */
    export function identity(out: mat3): mat3;
    /**
     * Transpose the values of a mat3
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the source matrix
     * @returns {mat3} out
     */
    export function transpose(out: mat3, a: mat3): mat3;
    /**
     * Inverts a mat3
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the source matrix
     * @returns {mat3} out
     */
    export function invert(out: mat3, a: mat3): mat3;
    /**
     * Calculates the adjugate of a mat3
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the source matrix
     * @returns {mat3} out
     */
    export function adjoint(out: mat3, a: mat3): mat3;
    /**
     * Calculates the determinant of a mat3
     *
     * @param {mat3} a the source matrix
     * @returns {Number} determinant of a
     */
    export function determinant(a: mat3): number;
    /**
     * Multiplies two mat3's
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the first operand
     * @param {mat3} b the second operand
     * @returns {mat3} out
     */
    export function multiply(out: mat3, a: mat3, b: mat3): mat3;
    /**
     * Translate a mat3 by the given vector
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the matrix to translate
     * @param {vec2} v vector to translate by
     * @returns {mat3} out
     */
    export function translate(out: mat3, a: mat3, v: vec2): mat3;
    /**
     * Rotates a mat3 by the given angle
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat3} out
     */
    export function rotate(out: mat3, a: mat3, rad: number): mat3;
    /**
     * Scales the mat3 by the dimensions in the given vec2
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the matrix to rotate
     * @param {vec2} v the vec2 to scale the matrix by
     * @returns {mat3} out
     **/
    export function scale(out: mat3, a: mat3, v: vec2): mat3;
    /**
     * Creates a matrix from a vector translation
     * This is equivalent to (but much faster than):
     *
     *     mat3.identity(dest);
     *     mat3.translate(dest, dest, vec);
     *
     * @param {mat3} out mat3 receiving operation result
     * @param {vec2} v Translation vector
     * @returns {mat3} out
     */
    export function fromTranslation(out: mat3, v: vec2): mat3;
    /**
     * Creates a matrix from a given angle
     * This is equivalent to (but much faster than):
     *
     *     mat3.identity(dest);
     *     mat3.rotate(dest, dest, rad);
     *
     * @param {mat3} out mat3 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat3} out
     */
    export function fromRotation(out: mat3, rad: number): mat3;
    /**
     * Creates a matrix from a vector scaling
     * This is equivalent to (but much faster than):
     *
     *     mat3.identity(dest);
     *     mat3.scale(dest, dest, vec);
     *
     * @param {mat3} out mat3 receiving operation result
     * @param {vec2} v Scaling vector
     * @returns {mat3} out
     */
    export function fromScaling(out: mat3, v: vec2): mat3;
    /**
     * Copies the values from a mat2d into a mat3
     *
     * @param {mat3} out the receiving matrix
     * @param {mat2d} a the matrix to copy
     * @returns {mat3} out
     **/
    export function fromMat2d(out: mat3, a: mat2d): mat3;
    /**
     * Calculates a 3x3 matrix from the given quaternion
     *
     * @param {mat3} out mat3 receiving operation result
     * @param {quat} q Quaternion to create matrix from
     *
     * @returns {mat3} out
     */
    export function fromQuat(out: mat3, q: quat): mat3;
    /**
     * Calculates a 3x3 normal matrix (transpose inverse) from the 4x4 matrix
     *
     * @param {mat3} out mat3 receiving operation result
     * @param {mat4} a Mat4 to derive the normal matrix from
     *
     * @returns {mat3} out
     */
    export function normalFromMat4(out: mat3, a: mat4): mat3;
    /**
     * Generates a 2D projection matrix with the given bounds
     *
     * @param {mat3} out mat3 frustum matrix will be written into
     * @param {number} width Width of your gl context
     * @param {number} height Height of gl context
     * @returns {mat3} out
     */
    export function projection(out: mat3, width: number, height: number): mat3;
    /**
     * Returns a string representation of a mat3
     *
     * @param {mat3} a matrix to represent as a string
     * @returns {String} string representation of the matrix
     */
    export function str(a: mat3): string;
    /**
     * Returns Frobenius norm of a mat3
     *
     * @param {mat3} a the matrix to calculate Frobenius norm of
     * @returns {Number} Frobenius norm
     */
    export function frob(a: mat3): number;
    /**
     * Adds two mat3's
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the first operand
     * @param {mat3} b the second operand
     * @returns {mat3} out
     */
    export function add(out: mat3, a: mat3, b: mat3): mat3;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the first operand
     * @param {mat3} b the second operand
     * @returns {mat3} out
     */
    export function subtract(out: mat3, a: mat3, b: mat3): mat3;
    /**
     * Multiply each element of the matrix by a scalar.
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the matrix to scale
     * @param {Number} b amount to scale the matrix's elements by
     * @returns {mat3} out
     */
    export function multiplyScalar(out: mat3, a: mat3, b: number): mat3;
    /**
     * Adds two mat3's after multiplying each element of the second operand by a scalar value.
     *
     * @param {mat3} out the receiving vector
     * @param {mat3} a the first operand
     * @param {mat3} b the second operand
     * @param {Number} scale the amount to scale b's elements by before adding
     * @returns {mat3} out
     */
    export function multiplyScalarAndAdd(out: mat3, a: mat3, b: mat3, scale: number): mat3;
    /**
     * Returns whether or not the matrices have exactly the same elements in the same position (when compared with ===)
     *
     * @param {mat3} a The first matrix.
     * @param {mat3} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    export function exactEquals(a: mat3, b: mat3): boolean;
    /**
     * Returns whether or not the matrices have approximately the same elements in the same position.
     *
     * @param {mat3} a The first matrix.
     * @param {mat3} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    export function equals(a: mat3, b: mat3): boolean;
    /**
     * Multiplies two mat3's
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the first operand
     * @param {mat3} b the second operand
     * @returns {mat3} out
     */
    export function mul(out: mat3, a: mat3, b: mat3): mat3;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat3} out the receiving matrix
     * @param {mat3} a the first operand
     * @param {mat3} b the second operand
     * @returns {mat3} out
     */
    export function sub(out: mat3, a: mat3, b: mat3): mat3;
}
export module mat4 {
    /**
     * 4x4 Matrix<br>Format: column-major, when typed out it looks like row-major<br>The matrices are being post multiplied.
     * @module mat4
     */
    /**
     * Creates a new identity mat4
     *
     * @returns {mat4} a new 4x4 matrix
     */
    export function create(): mat4;
    /**
     * Creates a new mat4 initialized with values from an existing matrix
     *
     * @param {mat4} a matrix to clone
     * @returns {mat4} a new 4x4 matrix
     */
    export function clone(a: mat4): mat4;
    /**
     * Copy the values from one mat4 to another
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the source matrix
     * @returns {mat4} out
     */
    export function copy(out: mat4, a: mat4): mat4;
    /**
     * Create a new mat4 with the given values
     *
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m02 Component in column 0, row 2 position (index 2)
     * @param {Number} m03 Component in column 0, row 3 position (index 3)
     * @param {Number} m10 Component in column 1, row 0 position (index 4)
     * @param {Number} m11 Component in column 1, row 1 position (index 5)
     * @param {Number} m12 Component in column 1, row 2 position (index 6)
     * @param {Number} m13 Component in column 1, row 3 position (index 7)
     * @param {Number} m20 Component in column 2, row 0 position (index 8)
     * @param {Number} m21 Component in column 2, row 1 position (index 9)
     * @param {Number} m22 Component in column 2, row 2 position (index 10)
     * @param {Number} m23 Component in column 2, row 3 position (index 11)
     * @param {Number} m30 Component in column 3, row 0 position (index 12)
     * @param {Number} m31 Component in column 3, row 1 position (index 13)
     * @param {Number} m32 Component in column 3, row 2 position (index 14)
     * @param {Number} m33 Component in column 3, row 3 position (index 15)
     * @returns {mat4} A new mat4
     */
    export function fromValues(m00: number, m01: number, m02: number, m03: number, m10: number, m11: number, m12: number, m13: number, m20: number, m21: number, m22: number, m23: number, m30: number, m31: number, m32: number, m33: number): mat4;
    /**
     * Set the components of a mat4 to the given values
     *
     * @param {mat4} out the receiving matrix
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m02 Component in column 0, row 2 position (index 2)
     * @param {Number} m03 Component in column 0, row 3 position (index 3)
     * @param {Number} m10 Component in column 1, row 0 position (index 4)
     * @param {Number} m11 Component in column 1, row 1 position (index 5)
     * @param {Number} m12 Component in column 1, row 2 position (index 6)
     * @param {Number} m13 Component in column 1, row 3 position (index 7)
     * @param {Number} m20 Component in column 2, row 0 position (index 8)
     * @param {Number} m21 Component in column 2, row 1 position (index 9)
     * @param {Number} m22 Component in column 2, row 2 position (index 10)
     * @param {Number} m23 Component in column 2, row 3 position (index 11)
     * @param {Number} m30 Component in column 3, row 0 position (index 12)
     * @param {Number} m31 Component in column 3, row 1 position (index 13)
     * @param {Number} m32 Component in column 3, row 2 position (index 14)
     * @param {Number} m33 Component in column 3, row 3 position (index 15)
     * @returns {mat4} out
     */
    export function set(out: mat4, m00: number, m01: number, m02: number, m03: number, m10: number, m11: number, m12: number, m13: number, m20: number, m21: number, m22: number, m23: number, m30: number, m31: number, m32: number, m33: number): mat4;
    /**
     * Set a mat4 to the identity matrix
     *
     * @param {mat4} out the receiving matrix
     * @returns {mat4} out
     */
    export function identity(out: mat4): mat4;
    /**
     * Transpose the values of a mat4
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the source matrix
     * @returns {mat4} out
     */
    export function transpose(out: mat4, a: mat4): mat4;
    /**
     * Inverts a mat4
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the source matrix
     * @returns {mat4} out
     */
    export function invert(out: mat4, a: mat4): mat4;
    /**
     * Calculates the adjugate of a mat4
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the source matrix
     * @returns {mat4} out
     */
    export function adjoint(out: mat4, a: mat4): mat4;
    /**
     * Calculates the determinant of a mat4
     *
     * @param {mat4} a the source matrix
     * @returns {Number} determinant of a
     */
    export function determinant(a: mat4): number;
    /**
     * Multiplies two mat4s
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the first operand
     * @param {mat4} b the second operand
     * @returns {mat4} out
     */
    export function multiply(out: mat4, a: mat4, b: mat4): mat4;
    /**
     * Translate a mat4 by the given vector
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the matrix to translate
     * @param {vec3} v vector to translate by
     * @returns {mat4} out
     */
    export function translate(out: mat4, a: mat4, v: vec3): mat4;
    /**
     * Scales the mat4 by the dimensions in the given vec3 not using vectorization
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the matrix to scale
     * @param {vec3} v the vec3 to scale the matrix by
     * @returns {mat4} out
     **/
    export function scale(out: mat4, a: mat4, v: vec3): mat4;
    /**
     * Rotates a mat4 by the given angle around the given axis
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @param {vec3} axis the axis to rotate around
     * @returns {mat4} out
     */
    export function rotate(out: mat4, a: mat4, rad: number, axis: vec3): mat4;
    /**
     * Rotates a matrix by the given angle around the X axis
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    export function rotateX(out: mat4, a: mat4, rad: number): mat4;
    /**
     * Rotates a matrix by the given angle around the Y axis
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    export function rotateY(out: mat4, a: mat4, rad: number): mat4;
    /**
     * Rotates a matrix by the given angle around the Z axis
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    export function rotateZ(out: mat4, a: mat4, rad: number): mat4;
    /**
     * Creates a matrix from a vector translation
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.translate(dest, dest, vec);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {vec3} v Translation vector
     * @returns {mat4} out
     */
    export function fromTranslation(out: mat4, v: vec3): mat4;
    /**
     * Creates a matrix from a vector scaling
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.scale(dest, dest, vec);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {vec3} v Scaling vector
     * @returns {mat4} out
     */
    export function fromScaling(out: mat4, v: vec3): mat4;
    /**
     * Creates a matrix from a given angle around a given axis
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.rotate(dest, dest, rad, axis);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @param {vec3} axis the axis to rotate around
     * @returns {mat4} out
     */
    export function fromRotation(out: mat4, rad: number, axis: vec3): mat4;
    /**
     * Creates a matrix from the given angle around the X axis
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.rotateX(dest, dest, rad);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    export function fromXRotation(out: mat4, rad: number): mat4;
    /**
     * Creates a matrix from the given angle around the Y axis
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.rotateY(dest, dest, rad);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    export function fromYRotation(out: mat4, rad: number): mat4;
    /**
     * Creates a matrix from the given angle around the Z axis
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.rotateZ(dest, dest, rad);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    export function fromZRotation(out: mat4, rad: number): mat4;
    /**
     * Creates a matrix from a quaternion rotation and vector translation
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.translate(dest, vec);
     *     let quatMat = mat4.create();
     *     quat4.toMat4(quat, quatMat);
     *     mat4.multiply(dest, quatMat);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {quat4} q Rotation quaternion
     * @param {vec3} v Translation vector
     * @returns {mat4} out
     */
    export function fromRotationTranslation(out: mat4, q: any, v: vec3): mat4;
    /**
     * Creates a new mat4 from a dual quat.
     *
     * @param {mat4} out Matrix
     * @param {quat2} a Dual Quaternion
     * @returns {mat4} mat4 receiving operation result
     */
    export function fromQuat2(out: mat4, a: quat2): mat4;
    /**
     * Returns the translation vector component of a transformation
     *  matrix. If a matrix is built with fromRotationTranslation,
     *  the returned vector will be the same as the translation vector
     *  originally supplied.
     * @param  {vec3} out Vector to receive translation component
     * @param  {mat4} mat Matrix to be decomposed (input)
     * @return {vec3} out
     */
    export function getTranslation(out: vec3, mat: mat4): vec3;
    /**
     * Returns the scaling factor component of a transformation
     *  matrix. If a matrix is built with fromRotationTranslationScale
     *  with a normalized Quaternion paramter, the returned vector will be
     *  the same as the scaling vector
     *  originally supplied.
     * @param  {vec3} out Vector to receive scaling factor component
     * @param  {mat4} mat Matrix to be decomposed (input)
     * @return {vec3} out
     */
    export function getScaling(out: vec3, mat: mat4): vec3;
    /**
     * Returns a quaternion representing the rotational component
     *  of a transformation matrix. If a matrix is built with
     *  fromRotationTranslation, the returned quaternion will be the
     *  same as the quaternion originally supplied.
     * @param {quat} out Quaternion to receive the rotation component
     * @param {mat4} mat Matrix to be decomposed (input)
     * @return {quat} out
     */
    export function getRotation(out: quat, mat: mat4): quat;
    /**
     * Creates a matrix from a quaternion rotation, vector translation and vector scale
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.translate(dest, vec);
     *     let quatMat = mat4.create();
     *     quat4.toMat4(quat, quatMat);
     *     mat4.multiply(dest, quatMat);
     *     mat4.scale(dest, scale)
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {quat4} q Rotation quaternion
     * @param {vec3} v Translation vector
     * @param {vec3} s Scaling vector
     * @returns {mat4} out
     */
    export function fromRotationTranslationScale(out: mat4, q: any, v: vec3, s: vec3): mat4;
    /**
     * Creates a matrix from a quaternion rotation, vector translation and vector scale, rotating and scaling around the given origin
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.translate(dest, vec);
     *     mat4.translate(dest, origin);
     *     let quatMat = mat4.create();
     *     quat4.toMat4(quat, quatMat);
     *     mat4.multiply(dest, quatMat);
     *     mat4.scale(dest, scale)
     *     mat4.translate(dest, negativeOrigin);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {quat4} q Rotation quaternion
     * @param {vec3} v Translation vector
     * @param {vec3} s Scaling vector
     * @param {vec3} o The origin vector around which to scale and rotate
     * @returns {mat4} out
     */
    export function fromRotationTranslationScaleOrigin(out: mat4, q: any, v: vec3, s: vec3, o: vec3): mat4;
    /**
     * Calculates a 4x4 matrix from the given quaternion
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {quat} q Quaternion to create matrix from
     *
     * @returns {mat4} out
     */
    export function fromQuat(out: mat4, q: quat): mat4;
    /**
     * Generates a frustum matrix with the given bounds
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {Number} left Left bound of the frustum
     * @param {Number} right Right bound of the frustum
     * @param {Number} bottom Bottom bound of the frustum
     * @param {Number} top Top bound of the frustum
     * @param {Number} near Near bound of the frustum
     * @param {Number} far Far bound of the frustum
     * @returns {mat4} out
     */
    export function frustum(out: mat4, left: number, right: number, bottom: number, top: number, near: number, far: number): mat4;
    /**
     * Generates a perspective projection matrix with the given bounds.
     * Passing null/undefined/no value for far will generate infinite projection matrix.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {number} fovy Vertical field of view in radians
     * @param {number} aspect Aspect ratio. typically viewport width/height
     * @param {number} near Near bound of the frustum
     * @param {number} far Far bound of the frustum, can be null or Infinity
     * @returns {mat4} out
     */
    export function perspective(out: mat4, fovy: number, aspect: number, near: number, far: number): mat4;
    /**
     * Generates a perspective projection matrix with the given field of view.
     * This is primarily useful for generating projection matrices to be used
     * with the still experiemental WebVR API.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {Object} fov Object containing the following values: upDegrees, downDegrees, leftDegrees, rightDegrees
     * @param {number} near Near bound of the frustum
     * @param {number} far Far bound of the frustum
     * @returns {mat4} out
     */
    export function perspectiveFromFieldOfView(out: mat4, fov: any, near: number, far: number): mat4;
    /**
     * Generates a orthogonal projection matrix with the given bounds
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {number} left Left bound of the frustum
     * @param {number} right Right bound of the frustum
     * @param {number} bottom Bottom bound of the frustum
     * @param {number} top Top bound of the frustum
     * @param {number} near Near bound of the frustum
     * @param {number} far Far bound of the frustum
     * @returns {mat4} out
     */
    export function ortho(out: mat4, left: number, right: number, bottom: number, top: number, near: number, far: number): mat4;
    /**
     * Generates a look-at matrix with the given eye position, focal point, and up axis.
     * If you want a matrix that actually makes an object look at another object, you should use targetTo instead.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {vec3} eye Position of the viewer
     * @param {vec3} center Point the viewer is looking at
     * @param {vec3} up vec3 pointing up
     * @returns {mat4} out
     */
    export function lookAt(out: mat4, eye: vec3, center: vec3, up: vec3): mat4;
    /**
     * Generates a matrix that makes something look at something else.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {vec3} eye Position of the viewer
     * @param {vec3} center Point the viewer is looking at
     * @param {vec3} up vec3 pointing up
     * @returns {mat4} out
     */
    export function targetTo(out: mat4, eye: vec3, target: any, up: vec3): mat4;
    /**
     * Returns a string representation of a mat4
     *
     * @param {mat4} a matrix to represent as a string
     * @returns {String} string representation of the matrix
     */
    export function str(a: mat4): string;
    /**
     * Returns Frobenius norm of a mat4
     *
     * @param {mat4} a the matrix to calculate Frobenius norm of
     * @returns {Number} Frobenius norm
     */
    export function frob(a: mat4): number;
    /**
     * Adds two mat4's
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the first operand
     * @param {mat4} b the second operand
     * @returns {mat4} out
     */
    export function add(out: mat4, a: mat4, b: mat4): mat4;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the first operand
     * @param {mat4} b the second operand
     * @returns {mat4} out
     */
    export function subtract(out: mat4, a: mat4, b: mat4): mat4;
    /**
     * Multiply each element of the matrix by a scalar.
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the matrix to scale
     * @param {Number} b amount to scale the matrix's elements by
     * @returns {mat4} out
     */
    export function multiplyScalar(out: mat4, a: mat4, b: number): mat4;
    /**
     * Adds two mat4's after multiplying each element of the second operand by a scalar value.
     *
     * @param {mat4} out the receiving vector
     * @param {mat4} a the first operand
     * @param {mat4} b the second operand
     * @param {Number} scale the amount to scale b's elements by before adding
     * @returns {mat4} out
     */
    export function multiplyScalarAndAdd(out: mat4, a: mat4, b: mat4, scale: number): mat4;
    /**
     * Returns whether or not the matrices have exactly the same elements in the same position (when compared with ===)
     *
     * @param {mat4} a The first matrix.
     * @param {mat4} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    export function exactEquals(a: mat4, b: mat4): boolean;
    /**
     * Returns whether or not the matrices have approximately the same elements in the same position.
     *
     * @param {mat4} a The first matrix.
     * @param {mat4} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    export function equals(a: mat4, b: mat4): boolean;
    /**
     * Multiplies two mat4s
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the first operand
     * @param {mat4} b the second operand
     * @returns {mat4} out
     */
    export function mul(out: mat4, a: mat4, b: mat4): mat4;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat4} out the receiving matrix
     * @param {mat4} a the first operand
     * @param {mat4} b the second operand
     * @returns {mat4} out
     */
    export function sub(out: mat4, a: mat4, b: mat4): mat4;
}
export module vec3 {
    /**
     * 3 Dimensional Vector
     * @module vec3
     */
    /**
     * Creates a new, empty vec3
     *
     * @returns {vec3} a new 3D vector
     */
    export function create(): vec3;
    /**
     * Creates a new vec3 initialized with values from an existing vector
     *
     * @param {vec3} a vector to clone
     * @returns {vec3} a new 3D vector
     */
    export function clone(a: vec3): vec3;
    /**
     * Calculates the length of a vec3
     *
     * @param {vec3} a vector to calculate length of
     * @returns {Number} length of a
     */
    export function length(a: vec3): number;
    /**
     * Creates a new vec3 initialized with the given values
     *
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @returns {vec3} a new 3D vector
     */
    export function fromValues(x: number, y: number, z: number): vec3;
    /**
     * Copy the values from one vec3 to another
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the source vector
     * @returns {vec3} out
     */
    export function copy(out: vec3, a: vec3): vec3;
    /**
     * Set the components of a vec3 to the given values
     *
     * @param {vec3} out the receiving vector
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @returns {vec3} out
     */
    export function set(out: vec3, x: number, y: number, z: number): vec3;
    /**
     * Adds two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {vec3} out
     */
    export function add(out: vec3, a: vec3, b: vec3): vec3;
    /**
     * Subtracts vector b from vector a
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {vec3} out
     */
    export function subtract(out: vec3, a: vec3, b: vec3): vec3;
    /**
     * Multiplies two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {vec3} out
     */
    export function multiply(out: vec3, a: vec3, b: vec3): vec3;
    /**
     * Divides two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {vec3} out
     */
    export function divide(out: vec3, a: vec3, b: vec3): vec3;
    /**
     * Math.ceil the components of a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a vector to ceil
     * @returns {vec3} out
     */
    export function ceil(out: vec3, a: vec3): vec3;
    /**
     * Math.floor the components of a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a vector to floor
     * @returns {vec3} out
     */
    export function floor(out: vec3, a: vec3): vec3;
    /**
     * Returns the minimum of two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {vec3} out
     */
    export function min(out: vec3, a: vec3, b: vec3): vec3;
    /**
     * Returns the maximum of two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {vec3} out
     */
    export function max(out: vec3, a: vec3, b: vec3): vec3;
    /**
     * Math.round the components of a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a vector to round
     * @returns {vec3} out
     */
    export function round(out: vec3, a: vec3): vec3;
    /**
     * Scales a vec3 by a scalar number
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the vector to scale
     * @param {Number} b amount to scale the vector by
     * @returns {vec3} out
     */
    export function scale(out: vec3, a: vec3, b: number): vec3;
    /**
     * Adds two vec3's after scaling the second operand by a scalar value
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @param {Number} scale the amount to scale b by before adding
     * @returns {vec3} out
     */
    export function scaleAndAdd(out: vec3, a: vec3, b: vec3, scale: number): vec3;
    /**
     * Calculates the euclidian distance between two vec3's
     *
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {Number} distance between a and b
     */
    export function distance(a: vec3, b: vec3): number;
    /**
     * Calculates the squared euclidian distance between two vec3's
     *
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {Number} squared distance between a and b
     */
    export function squaredDistance(a: vec3, b: vec3): number;
    /**
     * Calculates the squared length of a vec3
     *
     * @param {vec3} a vector to calculate squared length of
     * @returns {Number} squared length of a
     */
    export function squaredLength(a: vec3): number;
    /**
     * Negates the components of a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a vector to negate
     * @returns {vec3} out
     */
    export function negate(out: vec3, a: vec3): vec3;
    /**
     * Returns the inverse of the components of a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a vector to invert
     * @returns {vec3} out
     */
    export function inverse(out: vec3, a: vec3): vec3;
    /**
     * Normalize a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a vector to normalize
     * @returns {vec3} out
     */
    export function normalize(out: vec3, a: vec3): vec3;
    /**
     * Calculates the dot product of two vec3's
     *
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {Number} dot product of a and b
     */
    export function dot(a: vec3, b: vec3): number;
    /**
     * Computes the cross product of two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {vec3} out
     */
    export function cross(out: vec3, a: vec3, b: vec3): vec3;
    /**
     * Performs a linear interpolation between two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {vec3} out
     */
    export function lerp(out: vec3, a: vec3, b: vec3, t: number): vec3;
    /**
     * Performs a hermite interpolation with two control points
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @param {vec3} c the third operand
     * @param {vec3} d the fourth operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {vec3} out
     */
    export function hermite(out: vec3, a: vec3, b: vec3, c: vec3, d: vec3, t: number): vec3;
    /**
     * Performs a bezier interpolation with two control points
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @param {vec3} c the third operand
     * @param {vec3} d the fourth operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {vec3} out
     */
    export function bezier(out: vec3, a: vec3, b: vec3, c: vec3, d: vec3, t: number): vec3;
    /**
     * Generates a random vector with the given scale
     *
     * @param {vec3} out the receiving vector
     * @param {Number} [scale] Length of the resulting vector. If ommitted, a unit vector will be returned
     * @returns {vec3} out
     */
    export function random(out: vec3, scale?: number): vec3;
    /**
     * Transforms the vec3 with a mat4.
     * 4th vector component is implicitly '1'
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the vector to transform
     * @param {mat4} m matrix to transform with
     * @returns {vec3} out
     */
    export function transformMat4(out: vec3, a: vec3, m: mat4): vec3;
    /**
     * Transforms the vec3 with a mat3.
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the vector to transform
     * @param {mat3} m the 3x3 matrix to transform with
     * @returns {vec3} out
     */
    export function transformMat3(out: vec3, a: vec3, m: mat3): vec3;
    /**
     * Transforms the vec3 with a quat
     * Can also be used for dual quaternions. (Multiply it with the real part)
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the vector to transform
     * @param {quat} q quaternion to transform with
     * @returns {vec3} out
     */
    export function transformQuat(out: vec3, a: vec3, q: quat): vec3;
    /**
     * Rotate a 3D vector around the x-axis
     * @param {vec3} out The receiving vec3
     * @param {vec3} a The vec3 point to rotate
     * @param {vec3} b The origin of the rotation
     * @param {Number} rad The angle of rotation in radians
     * @returns {vec3} out
     */
    export function rotateX(out: vec3, a: vec3, b: vec3, rad: number): vec3;
    /**
     * Rotate a 3D vector around the y-axis
     * @param {vec3} out The receiving vec3
     * @param {vec3} a The vec3 point to rotate
     * @param {vec3} b The origin of the rotation
     * @param {Number} rad The angle of rotation in radians
     * @returns {vec3} out
     */
    export function rotateY(out: vec3, a: vec3, b: vec3, rad: number): vec3;
    /**
     * Rotate a 3D vector around the z-axis
     * @param {vec3} out The receiving vec3
     * @param {vec3} a The vec3 point to rotate
     * @param {vec3} b The origin of the rotation
     * @param {Number} rad The angle of rotation in radians
     * @returns {vec3} out
     */
    export function rotateZ(out: vec3, a: vec3, b: vec3, rad: number): vec3;
    /**
     * Get the angle between two 3D vectors
     * @param {vec3} a The first operand
     * @param {vec3} b The second operand
     * @returns {Number} The angle in radians
     */
    export function angle(a: vec3, b: vec3): number;
    /**
     * Set the components of a vec3 to zero
     *
     * @param {vec3} out the receiving vector
     * @returns {vec3} out
     */
    export function zero(out: vec3): vec3;
    /**
     * Returns a string representation of a vector
     *
     * @param {vec3} a vector to represent as a string
     * @returns {String} string representation of the vector
     */
    export function str(a: vec3): string;
    /**
     * Returns whether or not the vectors have exactly the same elements in the same position (when compared with ===)
     *
     * @param {vec3} a The first vector.
     * @param {vec3} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    export function exactEquals(a: vec3, b: vec3): boolean;
    /**
     * Returns whether or not the vectors have approximately the same elements in the same position.
     *
     * @param {vec3} a The first vector.
     * @param {vec3} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    export function equals(a: vec3, b: vec3): boolean;
    /**
     * Subtracts vector b from vector a
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {vec3} out
     */
    export function sub(out: vec3, a: vec3, b: vec3): vec3;
    /**
     * Multiplies two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {vec3} out
     */
    export function mul(out: vec3, a: vec3, b: vec3): vec3;
    /**
     * Divides two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {vec3} out
     */
    export function div(out: vec3, a: vec3, b: vec3): vec3;
    /**
     * Calculates the euclidian distance between two vec3's
     *
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {Number} distance between a and b
     */
    export function dist(a: vec3, b: vec3): number;
    /**
     * Calculates the squared euclidian distance between two vec3's
     *
     * @param {vec3} a the first operand
     * @param {vec3} b the second operand
     * @returns {Number} squared distance between a and b
     */
    export function sqrDist(a: vec3, b: vec3): number;
    /**
     * Calculates the length of a vec3
     *
     * @param {vec3} a vector to calculate length of
     * @returns {Number} length of a
     */
    export function len(a: vec3): number;
    /**
     * Calculates the squared length of a vec3
     *
     * @param {vec3} a vector to calculate squared length of
     * @returns {Number} squared length of a
     */
    export function sqrLen(a: vec3): number;
    export function forEach(a: any, stride: any, offset: any, count: any, fn: any, arg: any): any;
}
export module vec4 {
    /**
     * 4 Dimensional Vector
     * @module vec4
     */
    /**
     * Creates a new, empty vec4
     *
     * @returns {vec4} a new 4D vector
     */
    export function create(): vec4;
    /**
     * Creates a new vec4 initialized with values from an existing vector
     *
     * @param {vec4} a vector to clone
     * @returns {vec4} a new 4D vector
     */
    export function clone(a: vec4): vec4;
    /**
     * Creates a new vec4 initialized with the given values
     *
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @param {Number} w W component
     * @returns {vec4} a new 4D vector
     */
    export function fromValues(x: number, y: number, z: number, w: number): vec4;
    /**
     * Copy the values from one vec4 to another
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the source vector
     * @returns {vec4} out
     */
    export function copy(out: vec4, a: vec4): vec4;
    /**
     * Set the components of a vec4 to the given values
     *
     * @param {vec4} out the receiving vector
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @param {Number} w W component
     * @returns {vec4} out
     */
    export function set(out: vec4, x: number, y: number, z: number, w: number): vec4;
    /**
     * Adds two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {vec4} out
     */
    export function add(out: vec4, a: vec4, b: vec4): vec4;
    /**
     * Subtracts vector b from vector a
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {vec4} out
     */
    export function subtract(out: vec4, a: vec4, b: vec4): vec4;
    /**
     * Multiplies two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {vec4} out
     */
    export function multiply(out: vec4, a: vec4, b: vec4): vec4;
    /**
     * Divides two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {vec4} out
     */
    export function divide(out: vec4, a: vec4, b: vec4): vec4;
    /**
     * Math.ceil the components of a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a vector to ceil
     * @returns {vec4} out
     */
    export function ceil(out: vec4, a: vec4): vec4;
    /**
     * Math.floor the components of a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a vector to floor
     * @returns {vec4} out
     */
    export function floor(out: vec4, a: vec4): vec4;
    /**
     * Returns the minimum of two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {vec4} out
     */
    export function min(out: vec4, a: vec4, b: vec4): vec4;
    /**
     * Returns the maximum of two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {vec4} out
     */
    export function max(out: vec4, a: vec4, b: vec4): vec4;
    /**
     * Math.round the components of a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a vector to round
     * @returns {vec4} out
     */
    export function round(out: vec4, a: vec4): vec4;
    /**
     * Scales a vec4 by a scalar number
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the vector to scale
     * @param {Number} b amount to scale the vector by
     * @returns {vec4} out
     */
    export function scale(out: vec4, a: vec4, b: number): vec4;
    /**
     * Adds two vec4's after scaling the second operand by a scalar value
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @param {Number} scale the amount to scale b by before adding
     * @returns {vec4} out
     */
    export function scaleAndAdd(out: vec4, a: vec4, b: vec4, scale: number): vec4;
    /**
     * Calculates the euclidian distance between two vec4's
     *
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {Number} distance between a and b
     */
    export function distance(a: vec4, b: vec4): number;
    /**
     * Calculates the squared euclidian distance between two vec4's
     *
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {Number} squared distance between a and b
     */
    export function squaredDistance(a: vec4, b: vec4): number;
    /**
     * Calculates the length of a vec4
     *
     * @param {vec4} a vector to calculate length of
     * @returns {Number} length of a
     */
    export function length(a: vec4): number;
    /**
     * Calculates the squared length of a vec4
     *
     * @param {vec4} a vector to calculate squared length of
     * @returns {Number} squared length of a
     */
    export function squaredLength(a: vec4): number;
    /**
     * Negates the components of a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a vector to negate
     * @returns {vec4} out
     */
    export function negate(out: vec4, a: vec4): vec4;
    /**
     * Returns the inverse of the components of a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a vector to invert
     * @returns {vec4} out
     */
    export function inverse(out: vec4, a: vec4): vec4;
    /**
     * Normalize a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a vector to normalize
     * @returns {vec4} out
     */
    export function normalize(out: vec4, a: vec4): vec4;
    /**
     * Calculates the dot product of two vec4's
     *
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {Number} dot product of a and b
     */
    export function dot(a: vec4, b: vec4): number;
    /**
     * Returns the cross-product of three vectors in a 4-dimensional space
     *
     * @param {vec4} result the receiving vector
     * @param {vec4} U the first vector
     * @param {vec4} V the second vector
     * @param {vec4} W the third vector
     * @returns {vec4} result
     */
    export function cross(out: any, u: any, v: any, w: any): vec4;
    /**
     * Performs a linear interpolation between two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {vec4} out
     */
    export function lerp(out: vec4, a: vec4, b: vec4, t: number): vec4;
    /**
     * Generates a random vector with the given scale
     *
     * @param {vec4} out the receiving vector
     * @param {Number} [scale] Length of the resulting vector. If ommitted, a unit vector will be returned
     * @returns {vec4} out
     */
    export function random(out: vec4, scale?: number): vec4;
    /**
     * Transforms the vec4 with a mat4.
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the vector to transform
     * @param {mat4} m matrix to transform with
     * @returns {vec4} out
     */
    export function transformMat4(out: vec4, a: vec4, m: mat4): vec4;
    /**
     * Transforms the vec4 with a quat
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the vector to transform
     * @param {quat} q quaternion to transform with
     * @returns {vec4} out
     */
    export function transformQuat(out: vec4, a: vec4, q: quat): vec4;
    /**
     * Set the components of a vec4 to zero
     *
     * @param {vec4} out the receiving vector
     * @returns {vec4} out
     */
    export function zero(out: vec4): vec4;
    /**
     * Returns a string representation of a vector
     *
     * @param {vec4} a vector to represent as a string
     * @returns {String} string representation of the vector
     */
    export function str(a: vec4): string;
    /**
     * Returns whether or not the vectors have exactly the same elements in the same position (when compared with ===)
     *
     * @param {vec4} a The first vector.
     * @param {vec4} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    export function exactEquals(a: vec4, b: vec4): boolean;
    /**
     * Returns whether or not the vectors have approximately the same elements in the same position.
     *
     * @param {vec4} a The first vector.
     * @param {vec4} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    export function equals(a: vec4, b: vec4): boolean;
    /**
     * Subtracts vector b from vector a
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {vec4} out
     */
    export function sub(out: vec4, a: vec4, b: vec4): vec4;
    /**
     * Multiplies two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {vec4} out
     */
    export function mul(out: vec4, a: vec4, b: vec4): vec4;
    /**
     * Divides two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {vec4} out
     */
    export function div(out: vec4, a: vec4, b: vec4): vec4;
    /**
     * Calculates the euclidian distance between two vec4's
     *
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {Number} distance between a and b
     */
    export function dist(a: vec4, b: vec4): number;
    /**
     * Calculates the squared euclidian distance between two vec4's
     *
     * @param {vec4} a the first operand
     * @param {vec4} b the second operand
     * @returns {Number} squared distance between a and b
     */
    export function sqrDist(a: vec4, b: vec4): number;
    /**
     * Calculates the length of a vec4
     *
     * @param {vec4} a vector to calculate length of
     * @returns {Number} length of a
     */
    export function len(a: vec4): number;
    /**
     * Calculates the squared length of a vec4
     *
     * @param {vec4} a vector to calculate squared length of
     * @returns {Number} squared length of a
     */
    export function sqrLen(a: vec4): number;
    export function forEach(a: any, stride: any, offset: any, count: any, fn: any, arg: any): any;
}
export module quat {
    /**
     * Quaternion
     * @module quat
     */
    /**
     * Creates a new identity quat
     *
     * @returns {quat} a new quaternion
     */
    export function create(): quat;
    /**
     * Set a quat to the identity quaternion
     *
     * @param {quat} out the receiving quaternion
     * @returns {quat} out
     */
    export function identity(out: quat): quat;
    /**
     * Sets a quat from the given angle and rotation axis,
     * then returns it.
     *
     * @param {quat} out the receiving quaternion
     * @param {vec3} axis the axis around which to rotate
     * @param {Number} rad the angle in radians
     * @returns {quat} out
     **/
    export function setAxisAngle(out: quat, axis: vec3, rad: number): quat;
    /**
     * Gets the rotation axis and angle for a given
     *  quaternion. If a quaternion is created with
     *  setAxisAngle, this method will return the same
     *  values as providied in the original parameter list
     *  OR functionally equivalent values.
     * Example: The quaternion formed by axis [0, 0, 1] and
     *  angle -90 is the same as the quaternion formed by
     *  [0, 0, 1] and 270. This method favors the latter.
     * @param  {vec3} out_axis  Vector receiving the axis of rotation
     * @param  {quat} q     Quaternion to be decomposed
     * @return {Number}     Angle, in radians, of the rotation
     */
    export function getAxisAngle(out_axis: vec3, q: quat): number;
    /**
     * Gets the angular distance between two unit quaternions
     *
     * @param  {quat} a     Origin unit quaternion
     * @param  {quat} b     Destination unit quaternion
     * @return {Number}     Angle, in radians, between the two quaternions
     */
    export function getAngle(a: quat, b: quat): number;
    /**
     * Multiplies two quat's
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a the first operand
     * @param {quat} b the second operand
     * @returns {quat} out
     */
    export function multiply(out: quat, a: quat, b: quat): quat;
    /**
     * Rotates a quaternion by the given angle about the X axis
     *
     * @param {quat} out quat receiving operation result
     * @param {quat} a quat to rotate
     * @param {number} rad angle (in radians) to rotate
     * @returns {quat} out
     */
    export function rotateX(out: quat, a: quat, rad: number): quat;
    /**
     * Rotates a quaternion by the given angle about the Y axis
     *
     * @param {quat} out quat receiving operation result
     * @param {quat} a quat to rotate
     * @param {number} rad angle (in radians) to rotate
     * @returns {quat} out
     */
    export function rotateY(out: quat, a: quat, rad: number): quat;
    /**
     * Rotates a quaternion by the given angle about the Z axis
     *
     * @param {quat} out quat receiving operation result
     * @param {quat} a quat to rotate
     * @param {number} rad angle (in radians) to rotate
     * @returns {quat} out
     */
    export function rotateZ(out: quat, a: quat, rad: number): quat;
    /**
     * Calculates the W component of a quat from the X, Y, and Z components.
     * Assumes that quaternion is 1 unit in length.
     * Any existing W component will be ignored.
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a quat to calculate W component of
     * @returns {quat} out
     */
    export function calculateW(out: quat, a: quat): quat;
    /**
     * Calculate the exponential of a unit quaternion.
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a quat to calculate the exponential of
     * @returns {quat} out
     */
    export function exp(out: quat, a: quat): quat;
    /**
     * Calculate the natural logarithm of a unit quaternion.
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a quat to calculate the exponential of
     * @returns {quat} out
     */
    export function ln(out: quat, a: quat): quat;
    /**
     * Calculate the scalar power of a unit quaternion.
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a quat to calculate the exponential of
     * @param {Number} b amount to scale the quaternion by
     * @returns {quat} out
     */
    export function pow(out: quat, a: quat, b: number): quat;
    /**
     * Performs a spherical linear interpolation between two quat
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a the first operand
     * @param {quat} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {quat} out
     */
    export function slerp(out: quat, a: quat, b: quat, t: number): quat;
    /**
     * Generates a random unit quaternion
     *
     * @param {quat} out the receiving quaternion
     * @returns {quat} out
     */
    export function random(out: quat): quat;
    /**
     * Calculates the inverse of a quat
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a quat to calculate inverse of
     * @returns {quat} out
     */
    export function invert(out: quat, a: quat): quat;
    /**
     * Calculates the conjugate of a quat
     * If the quaternion is normalized, this function is faster than quat.inverse and produces the same result.
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a quat to calculate conjugate of
     * @returns {quat} out
     */
    export function conjugate(out: quat, a: quat): quat;
    /**
     * Creates a quaternion from the given 3x3 rotation matrix.
     *
     * NOTE: The resultant quaternion is not normalized, so you should be sure
     * to renormalize the quaternion yourself where necessary.
     *
     * @param {quat} out the receiving quaternion
     * @param {mat3} m rotation matrix
     * @returns {quat} out
     * @function
     */
    export function fromMat3(out: quat, m: mat3): quat;
    /**
     * Creates a quaternion from the given euler angle x, y, z.
     *
     * @param {quat} out the receiving quaternion
     * @param {x} Angle to rotate around X axis in degrees.
     * @param {y} Angle to rotate around Y axis in degrees.
     * @param {z} Angle to rotate around Z axis in degrees.
     * @returns {quat} out
     * @function
     */
    export function fromEuler(out: quat, x: any, y: any, z: any): quat;
    /**
     * Returns a string representation of a quatenion
     *
     * @param {quat} a vector to represent as a string
     * @returns {String} string representation of the vector
     */
    export function str(a: quat): string;
    /**
     * Creates a new quat initialized with values from an existing quaternion
     *
     * @param {quat} a quaternion to clone
     * @returns {quat} a new quaternion
     * @function
     */
    export const clone: typeof vec4.clone;
    /**
     * Creates a new quat initialized with the given values
     *
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @param {Number} w W component
     * @returns {quat} a new quaternion
     * @function
     */
    export const fromValues: typeof vec4.fromValues;
    /**
     * Copy the values from one quat to another
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a the source quaternion
     * @returns {quat} out
     * @function
     */
    export const copy: typeof vec4.copy;
    /**
     * Set the components of a quat to the given values
     *
     * @param {quat} out the receiving quaternion
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @param {Number} w W component
     * @returns {quat} out
     * @function
     */
    export const set: typeof vec4.set;
    /**
     * Adds two quat's
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a the first operand
     * @param {quat} b the second operand
     * @returns {quat} out
     * @function
     */
    export const add: typeof vec4.add;
    /**
     * Multiplies two quat's
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a the first operand
     * @param {quat} b the second operand
     * @returns {quat} out
     */
    export function mul(out: quat, a: quat, b: quat): quat;
    /**
     * Scales a quat by a scalar number
     *
     * @param {quat} out the receiving vector
     * @param {quat} a the vector to scale
     * @param {Number} b amount to scale the vector by
     * @returns {quat} out
     * @function
     */
    export const scale: typeof vec4.scale;
    /**
     * Calculates the dot product of two quat's
     *
     * @param {quat} a the first operand
     * @param {quat} b the second operand
     * @returns {Number} dot product of a and b
     * @function
     */
    export const dot: typeof vec4.dot;
    /**
     * Performs a linear interpolation between two quat's
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a the first operand
     * @param {quat} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {quat} out
     * @function
     */
    export const lerp: typeof vec4.lerp;
    /**
     * Calculates the length of a quat
     *
     * @param {quat} a vector to calculate length of
     * @returns {Number} length of a
     */
    export const length: typeof vec4.length;
    /**
     * Alias for {@link quat.length}
     * @function
     */
    export const len: typeof vec4.length;
    /**
     * Calculates the squared length of a quat
     *
     * @param {quat} a vector to calculate squared length of
     * @returns {Number} squared length of a
     * @function
     */
    export const squaredLength: typeof vec4.squaredLength;
    /**
     * Alias for {@link quat.squaredLength}
     * @function
     */
    export const sqrLen: typeof vec4.squaredLength;
    /**
     * Normalize a quat
     *
     * @param {quat} out the receiving quaternion
     * @param {quat} a quaternion to normalize
     * @returns {quat} out
     * @function
     */
    export const normalize: typeof vec4.normalize;
    /**
     * Returns whether or not the quaternions have exactly the same elements in the same position (when compared with ===)
     *
     * @param {quat} a The first quaternion.
     * @param {quat} b The second quaternion.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    export const exactEquals: typeof vec4.exactEquals;
    /**
     * Returns whether or not the quaternions have approximately the same elements in the same position.
     *
     * @param {quat} a The first vector.
     * @param {quat} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    export const equals: typeof vec4.equals;
    export function rotationTo(out: any, a: any, b: any): any;
    export function sqlerp(out: any, a: any, b: any, c: any, d: any, t: any): any;
    export function setAxes(out: any, view: any, right: any, up: any): vec4;

}
export module quat2 {
    /**
     * Dual Quaternion<br>
     * Format: [real, dual]<br>
     * Quaternion format: XYZW<br>
     * Make sure to have normalized dual quaternions, otherwise the functions may not work as intended.<br>
     * @module quat2
     */
    /**
     * Creates a new identity dual quat
     *
     * @returns {quat2} a new dual quaternion [real -> rotation, dual -> translation]
     */
    export function create(): quat2;
    /**
     * Creates a new quat initialized with values from an existing quaternion
     *
     * @param {quat2} a dual quaternion to clone
     * @returns {quat2} new dual quaternion
     * @function
     */
    export function clone(a: quat2): quat2;
    /**
     * Creates a new dual quat initialized with the given values
     *
     * @param {Number} x1 X component
     * @param {Number} y1 Y component
     * @param {Number} z1 Z component
     * @param {Number} w1 W component
     * @param {Number} x2 X component
     * @param {Number} y2 Y component
     * @param {Number} z2 Z component
     * @param {Number} w2 W component
     * @returns {quat2} new dual quaternion
     * @function
     */
    export function fromValues(x1: number, y1: number, z1: number, w1: number, x2: number, y2: number, z2: number, w2: number): quat2;
    /**
     * Creates a new dual quat from the given values (quat and translation)
     *
     * @param {Number} x1 X component
     * @param {Number} y1 Y component
     * @param {Number} z1 Z component
     * @param {Number} w1 W component
     * @param {Number} x2 X component (translation)
     * @param {Number} y2 Y component (translation)
     * @param {Number} z2 Z component (translation)
     * @returns {quat2} new dual quaternion
     * @function
     */
    export function fromRotationTranslationValues(x1: number, y1: number, z1: number, w1: number, x2: number, y2: number, z2: number): quat2;
    /**
     * Creates a dual quat from a quaternion and a translation
     *
     * @param {quat2} dual quaternion receiving operation result
     * @param {quat} q a normalized quaternion
     * @param {vec3} t tranlation vector
     * @returns {quat2} dual quaternion receiving operation result
     * @function
     */
    export function fromRotationTranslation(out: any, q: quat, t: vec3): quat2;
    /**
     * Creates a dual quat from a translation
     *
     * @param {quat2} dual quaternion receiving operation result
     * @param {vec3} t translation vector
     * @returns {quat2} dual quaternion receiving operation result
     * @function
     */
    export function fromTranslation(out: any, t: vec3): quat2;
    /**
     * Creates a dual quat from a quaternion
     *
     * @param {quat2} dual quaternion receiving operation result
     * @param {quat} q the quaternion
     * @returns {quat2} dual quaternion receiving operation result
     * @function
     */
    export function fromRotation(out: any, q: quat): quat2;
    /**
     * Creates a new dual quat from a matrix (4x4)
     *
     * @param {quat2} out the dual quaternion
     * @param {mat4} a the matrix
     * @returns {quat2} dual quat receiving operation result
     * @function
     */
    export function fromMat4(out: quat2, a: mat4): quat2;
    /**
     * Copy the values from one dual quat to another
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a the source dual quaternion
     * @returns {quat2} out
     * @function
     */
    export function copy(out: quat2, a: quat2): quat2;
    /**
     * Set a dual quat to the identity dual quaternion
     *
     * @param {quat2} out the receiving quaternion
     * @returns {quat2} out
     */
    export function identity(out: quat2): quat2;
    /**
     * Set the components of a dual quat to the given values
     *
     * @param {quat2} out the receiving quaternion
     * @param {Number} x1 X component
     * @param {Number} y1 Y component
     * @param {Number} z1 Z component
     * @param {Number} w1 W component
     * @param {Number} x2 X component
     * @param {Number} y2 Y component
     * @param {Number} z2 Z component
     * @param {Number} w2 W component
     * @returns {quat2} out
     * @function
     */
    export function set(out: quat2, x1: number, y1: number, z1: number, w1: number, x2: number, y2: number, z2: number, w2: number): quat2;
    /**
     * Gets the dual part of a dual quat
     * @param  {quat} out dual part
     * @param  {quat2} a Dual Quaternion
     * @return {quat} dual part
     */
    export function getDual(out: quat, a: quat2): quat;
    /**
     * Set the dual component of a dual quat to the given quaternion
     *
     * @param {quat2} out the receiving quaternion
     * @param {quat} q a quaternion representing the dual part
     * @returns {quat2} out
     * @function
     */
    export function setDual(out: quat2, q: quat): quat2;
    /**
     * Gets the translation of a normalized dual quat
     * @param  {vec3} out translation
     * @param  {quat2} a Dual Quaternion to be decomposed
     * @return {vec3} translation
     */
    export function getTranslation(out: vec3, a: quat2): vec3;
    /**
     * Translates a dual quat by the given vector
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a the dual quaternion to translate
     * @param {vec3} v vector to translate by
     * @returns {quat2} out
     */
    export function translate(out: quat2, a: quat2, v: vec3): quat2;
    /**
     * Rotates a dual quat around the X axis
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a the dual quaternion to rotate
     * @param {number} rad how far should the rotation be
     * @returns {quat2} out
     */
    export function rotateX(out: quat2, a: quat2, rad: number): quat2;
    /**
     * Rotates a dual quat around the Y axis
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a the dual quaternion to rotate
     * @param {number} rad how far should the rotation be
     * @returns {quat2} out
     */
    export function rotateY(out: quat2, a: quat2, rad: number): quat2;
    /**
     * Rotates a dual quat around the Z axis
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a the dual quaternion to rotate
     * @param {number} rad how far should the rotation be
     * @returns {quat2} out
     */
    export function rotateZ(out: quat2, a: quat2, rad: number): quat2;
    /**
     * Rotates a dual quat by a given quaternion (a * q)
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a the dual quaternion to rotate
     * @param {quat} q quaternion to rotate by
     * @returns {quat2} out
     */
    export function rotateByQuatAppend(out: quat2, a: quat2, q: quat): quat2;
    /**
     * Rotates a dual quat by a given quaternion (q * a)
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat} q quaternion to rotate by
     * @param {quat2} a the dual quaternion to rotate
     * @returns {quat2} out
     */
    export function rotateByQuatPrepend(out: quat2, q: quat, a: quat2): quat2;
    /**
     * Rotates a dual quat around a given axis. Does the normalisation automatically
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a the dual quaternion to rotate
     * @param {vec3} axis the axis to rotate around
     * @param {Number} rad how far the rotation should be
     * @returns {quat2} out
     */
    export function rotateAroundAxis(out: quat2, a: quat2, axis: vec3, rad: number): quat2;
    /**
     * Adds two dual quat's
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a the first operand
     * @param {quat2} b the second operand
     * @returns {quat2} out
     * @function
     */
    export function add(out: quat2, a: quat2, b: quat2): quat2;
    /**
     * Multiplies two dual quat's
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a the first operand
     * @param {quat2} b the second operand
     * @returns {quat2} out
     */
    export function multiply(out: quat2, a: quat2, b: quat2): quat2;
    /**
     * Scales a dual quat by a scalar number
     *
     * @param {quat2} out the receiving dual quat
     * @param {quat2} a the dual quat to scale
     * @param {Number} b amount to scale the dual quat by
     * @returns {quat2} out
     * @function
     */
    export function scale(out: quat2, a: quat2, b: number): quat2;
    /**
     * Performs a linear interpolation between two dual quats's
     * NOTE: The resulting dual quaternions won't always be normalized (The error is most noticeable when t = 0.5)
     *
     * @param {quat2} out the receiving dual quat
     * @param {quat2} a the first operand
     * @param {quat2} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {quat2} out
     */
    export function lerp(out: quat2, a: quat2, b: quat2, t: number): quat2;
    /**
     * Calculates the inverse of a dual quat. If they are normalized, conjugate is cheaper
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a dual quat to calculate inverse of
     * @returns {quat2} out
     */
    export function invert(out: quat2, a: quat2): quat2;
    /**
     * Calculates the conjugate of a dual quat
     * If the dual quaternion is normalized, this function is faster than quat2.inverse and produces the same result.
     *
     * @param {quat2} out the receiving quaternion
     * @param {quat2} a quat to calculate conjugate of
     * @returns {quat2} out
     */
    export function conjugate(out: quat2, a: quat2): quat2;
    /**
     * Normalize a dual quat
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a dual quaternion to normalize
     * @returns {quat2} out
     * @function
     */
    export function normalize(out: quat2, a: quat2): quat2;
    /**
     * Returns a string representation of a dual quatenion
     *
     * @param {quat2} a dual quaternion to represent as a string
     * @returns {String} string representation of the dual quat
     */
    export function str(a: quat2): string;
    /**
     * Returns whether or not the dual quaternions have exactly the same elements in the same position (when compared with ===)
     *
     * @param {quat2} a the first dual quaternion.
     * @param {quat2} b the second dual quaternion.
     * @returns {Boolean} true if the dual quaternions are equal, false otherwise.
     */
    export function exactEquals(a: quat2, b: quat2): boolean;
    /**
     * Returns whether or not the dual quaternions have approximately the same elements in the same position.
     *
     * @param {quat2} a the first dual quat.
     * @param {quat2} b the second dual quat.
     * @returns {Boolean} true if the dual quats are equal, false otherwise.
     */
    export function equals(a: quat2, b: quat2): boolean;
    /**
     * Gets the real part of a dual quat
     * @param  {quat} out real part
     * @param  {quat2} a Dual Quaternion
     * @return {quat} real part
     */
    export const getReal: typeof vec4.copy;
    /**
     * Set the real component of a dual quat to the given quaternion
     *
     * @param {quat2} out the receiving quaternion
     * @param {quat} q a quaternion representing the real part
     * @returns {quat2} out
     * @function
     */
    export const setReal: typeof vec4.copy;
    /**
     * Multiplies two dual quat's
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {quat2} a the first operand
     * @param {quat2} b the second operand
     * @returns {quat2} out
     */
    export function mul(out: quat2, a: quat2, b: quat2): quat2;
    /**
     * Calculates the dot product of two dual quat's (The dot product of the real parts)
     *
     * @param {quat2} a the first operand
     * @param {quat2} b the second operand
     * @returns {Number} dot product of a and b
     * @function
     */
    export const dot: typeof vec4.dot;
    /**
     * Calculates the length of a dual quat
     *
     * @param {quat2} a dual quat to calculate length of
     * @returns {Number} length of a
     * @function
     */
    export const length: typeof vec4.length;
    /**
     * Alias for {@link quat2.length}
     * @function
     */
    export const len: typeof vec4.length;
    /**
     * Calculates the squared length of a dual quat
     *
     * @param {quat2} a dual quat to calculate squared length of
     * @returns {Number} squared length of a
     * @function
     */
    export const squaredLength: typeof vec4.squaredLength;
    /**
     * Alias for {@link quat2.squaredLength}
     * @function
     */
    export const sqrLen: typeof vec4.squaredLength;
}
export module vec2 {
    /**
     * 2 Dimensional Vector
     * @module vec2
     */
    /**
     * Creates a new, empty vec2
     *
     * @returns {vec2} a new 2D vector
     */
    export function create(): vec2;
    /**
     * Creates a new vec2 initialized with values from an existing vector
     *
     * @param {vec2} a vector to clone
     * @returns {vec2} a new 2D vector
     */
    export function clone(a: vec2): vec2;
    /**
     * Creates a new vec2 initialized with the given values
     *
     * @param {Number} x X component
     * @param {Number} y Y component
     * @returns {vec2} a new 2D vector
     */
    export function fromValues(x: number, y: number): vec2;
    /**
     * Copy the values from one vec2 to another
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the source vector
     * @returns {vec2} out
     */
    export function copy(out: vec2, a: vec2): vec2;
    /**
     * Set the components of a vec2 to the given values
     *
     * @param {vec2} out the receiving vector
     * @param {Number} x X component
     * @param {Number} y Y component
     * @returns {vec2} out
     */
    export function set(out: vec2, x: number, y: number): vec2;
    /**
     * Adds two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {vec2} out
     */
    export function add(out: vec2, a: vec2, b: vec2): vec2;
    /**
     * Subtracts vector b from vector a
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {vec2} out
     */
    export function subtract(out: vec2, a: vec2, b: vec2): vec2;
    /**
     * Multiplies two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {vec2} out
     */
    export function multiply(out: vec2, a: vec2, b: vec2): vec2;
    /**
     * Divides two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {vec2} out
     */
    export function divide(out: vec2, a: vec2, b: vec2): vec2;
    /**
     * Math.ceil the components of a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a vector to ceil
     * @returns {vec2} out
     */
    export function ceil(out: vec2, a: vec2): vec2;
    /**
     * Math.floor the components of a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a vector to floor
     * @returns {vec2} out
     */
    export function floor(out: vec2, a: vec2): vec2;
    /**
     * Returns the minimum of two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {vec2} out
     */
    export function min(out: vec2, a: vec2, b: vec2): vec2;
    /**
     * Returns the maximum of two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {vec2} out
     */
    export function max(out: vec2, a: vec2, b: vec2): vec2;
    /**
     * Math.round the components of a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a vector to round
     * @returns {vec2} out
     */
    export function round(out: vec2, a: vec2): vec2;
    /**
     * Scales a vec2 by a scalar number
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the vector to scale
     * @param {Number} b amount to scale the vector by
     * @returns {vec2} out
     */
    export function scale(out: vec2, a: vec2, b: number): vec2;
    /**
     * Adds two vec2's after scaling the second operand by a scalar value
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @param {Number} scale the amount to scale b by before adding
     * @returns {vec2} out
     */
    export function scaleAndAdd(out: vec2, a: vec2, b: vec2, scale: number): vec2;
    /**
     * Calculates the euclidian distance between two vec2's
     *
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {Number} distance between a and b
     */
    export function distance(a: vec2, b: vec2): number;
    /**
     * Calculates the squared euclidian distance between two vec2's
     *
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {Number} squared distance between a and b
     */
    export function squaredDistance(a: vec2, b: vec2): number;
    /**
     * Calculates the length of a vec2
     *
     * @param {vec2} a vector to calculate length of
     * @returns {Number} length of a
     */
    export function length(a: vec2): number;
    /**
     * Calculates the squared length of a vec2
     *
     * @param {vec2} a vector to calculate squared length of
     * @returns {Number} squared length of a
     */
    export function squaredLength(a: vec2): number;
    /**
     * Negates the components of a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a vector to negate
     * @returns {vec2} out
     */
    export function negate(out: vec2, a: vec2): vec2;
    /**
     * Returns the inverse of the components of a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a vector to invert
     * @returns {vec2} out
     */
    export function inverse(out: vec2, a: vec2): vec2;
    /**
     * Normalize a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a vector to normalize
     * @returns {vec2} out
     */
    export function normalize(out: vec2, a: vec2): vec2;
    /**
     * Calculates the dot product of two vec2's
     *
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {Number} dot product of a and b
     */
    export function dot(a: vec2, b: vec2): number;
    /**
     * Computes the cross product of two vec2's
     * Note that the cross product must by definition produce a 3D vector
     *
     * @param {vec3} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {vec3} out
     */
    export function cross(out: vec3, a: vec2, b: vec2): vec3;
    /**
     * Performs a linear interpolation between two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {vec2} out
     */
    export function lerp(out: vec2, a: vec2, b: vec2, t: number): vec2;
    /**
     * Generates a random vector with the given scale
     *
     * @param {vec2} out the receiving vector
     * @param {Number} [scale] Length of the resulting vector. If ommitted, a unit vector will be returned
     * @returns {vec2} out
     */
    export function random(out: vec2, scale?: number): vec2;
    /**
     * Transforms the vec2 with a mat2
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the vector to transform
     * @param {mat2} m matrix to transform with
     * @returns {vec2} out
     */
    export function transformMat2(out: vec2, a: vec2, m: mat2): vec2;
    /**
     * Transforms the vec2 with a mat2d
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the vector to transform
     * @param {mat2d} m matrix to transform with
     * @returns {vec2} out
     */
    export function transformMat2d(out: vec2, a: vec2, m: mat2d): vec2;
    /**
     * Transforms the vec2 with a mat3
     * 3rd vector component is implicitly '1'
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the vector to transform
     * @param {mat3} m matrix to transform with
     * @returns {vec2} out
     */
    export function transformMat3(out: vec2, a: vec2, m: mat3): vec2;
    /**
     * Transforms the vec2 with a mat4
     * 3rd vector component is implicitly '0'
     * 4th vector component is implicitly '1'
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the vector to transform
     * @param {mat4} m matrix to transform with
     * @returns {vec2} out
     */
    export function transformMat4(out: vec2, a: vec2, m: mat4): vec2;
    /**
     * Rotate a 2D vector
     * @param {vec2} out The receiving vec2
     * @param {vec2} a The vec2 point to rotate
     * @param {vec2} b The origin of the rotation
     * @param {Number} rad The angle of rotation in radians
     * @returns {vec2} out
     */
    export function rotate(out: vec2, a: vec2, b: vec2, rad: number): vec2;
    /**
     * Get the angle between two 2D vectors
     * @param {vec2} a The first operand
     * @param {vec2} b The second operand
     * @returns {Number} The angle in radians
     */
    export function angle(a: vec2, b: vec2): number;
    /**
     * Set the components of a vec2 to zero
     *
     * @param {vec2} out the receiving vector
     * @returns {vec2} out
     */
    export function zero(out: vec2): vec2;
    /**
     * Returns a string representation of a vector
     *
     * @param {vec2} a vector to represent as a string
     * @returns {String} string representation of the vector
     */
    export function str(a: vec2): string;
    /**
     * Returns whether or not the vectors exactly have the same elements in the same position (when compared with ===)
     *
     * @param {vec2} a The first vector.
     * @param {vec2} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    export function exactEquals(a: vec2, b: vec2): boolean;
    /**
     * Returns whether or not the vectors have approximately the same elements in the same position.
     *
     * @param {vec2} a The first vector.
     * @param {vec2} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    export function equals(a: vec2, b: vec2): boolean;
    /**
     * Calculates the length of a vec2
     *
     * @param {vec2} a vector to calculate length of
     * @returns {Number} length of a
     */
    export function len(a: vec2): number;
    /**
     * Subtracts vector b from vector a
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {vec2} out
     */
    export function sub(out: vec2, a: vec2, b: vec2): vec2;
    /**
     * Multiplies two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {vec2} out
     */
    export function mul(out: vec2, a: vec2, b: vec2): vec2;
    /**
     * Divides two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {vec2} out
     */
    export function div(out: vec2, a: vec2, b: vec2): vec2;
    /**
     * Calculates the euclidian distance between two vec2's
     *
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {Number} distance between a and b
     */
    export function dist(a: vec2, b: vec2): number;
    /**
     * Calculates the squared euclidian distance between two vec2's
     *
     * @param {vec2} a the first operand
     * @param {vec2} b the second operand
     * @returns {Number} squared distance between a and b
     */
    export function sqrDist(a: vec2, b: vec2): number;
    /**
     * Calculates the squared length of a vec2
     *
     * @param {vec2} a vector to calculate squared length of
     * @returns {Number} squared length of a
     */
    export function sqrLen(a: vec2): number;
    export function forEach(a: any, stride: any, offset: any, count: any, fn: any, arg: any): any;
}


}