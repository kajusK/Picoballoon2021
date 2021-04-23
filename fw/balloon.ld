/*
 * This file is part of the libopencm3 project.
 *
 * Copyright (C) 2015 Karl Palsson <karlp@tweak.net.au>
 *
 * This library is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library.  If not, see <http://www.gnu.org/licenses/>.
 */

/* Define memory regions. */
MEMORY
{
	rom (rx) : ORIGIN = 0x08000000, LENGTH = 60K
	ram (rwx) : ORIGIN = 0x20000000, LENGTH = 8K

	custom1(r) : ORIGIN = ORIGIN(rom) + LENGTH(rom), LENGTH = 2K
	custom2(r) : ORIGIN = ORIGIN(custom1) + LENGTH(custom1), LENGTH = LENGTH(custom1)
}

/** Custom areas for LoRa TX counter storage */
PROVIDE(counter1 = ORIGIN(custom1));
PROVIDE(counter2 = ORIGIN(custom2));

/* Include the common ld script. */
INCLUDE cortex-m-generic.ld