import ctypes
import pymem

kernel32 = ctypes.windll.kernel32


def get_address_from_offsets(process_handle, base, offsets, arch=32):
    size = 4 if arch == 32 else 8
    offsets = offsets if isinstance(offsets, list) else [offsets]

    address = ctypes.c_uint64(base)
    for offset in offsets:
        kernel32.ReadProcessMemory(process_handle, address, ctypes.byref(address), size, 0)
        address = ctypes.c_uint64(address.value + offset)

    return address.value


def change_sig_to_bytes(sig):
    sig = sig.replace("??", ".")
    return_byte = ""
    for byte in sig.split(" "):
        if byte != ".":
            return_byte += r"\x" + byte
        else:
            return_byte += "."
    return bytes(return_byte, "utf-8")


def get_address_from_sig(sig, process, extra=0, offset=0):
    sig = change_sig_to_bytes(sig)
    found_addresses = pymem.pattern.pattern_scan_all(process.process_handle, sig, return_multiple=True)
    if len(found_addresses) == 0:
        raise Exception("FAILED TO GET ADDRESS FROM SIG!!!")
    elif len(found_addresses) > 1:
        raise Exception("FOUND MORE THAN 1 ADDRESSES!!!!\n {}".format(str(found_addresses)))
    else:
        return process.read_int(found_addresses[0] + extra) + offset
