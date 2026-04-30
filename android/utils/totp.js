import CryptoJS from 'crypto-js'

export function parseSecret(input) {
	if (input.startsWith('otpauth://')) {
		try {
			const uri = new URL(input)
			const params = new URLSearchParams(uri.search)

			const secret = params.get('secret')
			if (!secret) {
				return { success: false, message: '未找到密钥参数' }
			}

			let digits = 6
			if (params.has('digits')) {
				const d = parseInt(params.get('digits'))
				if (d === 6 || d === 8) digits = d
			}

			let period = 30
			if (params.has('period')) {
				const p = parseInt(params.get('period'))
				if (p > 0) period = p
			}

			let algorithm = 'SHA1'
			if (params.has('algorithm')) {
				const alg = params.get('algorithm').toUpperCase()
				if (['SHA1', 'SHA256', 'SHA512'].includes(alg)) {
					algorithm = alg
				}
			}

			return {
				success: true,
				secret: secret.replace(/\s/g, '').toUpperCase(),
				digits,
				period,
				algorithm
			}
		} catch (e) {
			return { success: false, message: '无效的URI格式' }
		}
	}

	const cleanedSecret = input.replace(/\s/g, '').toUpperCase()

	if (!/^[A-Z2-7]+=*$/.test(cleanedSecret)) {
		return {
			success: true,
			secret: cleanedSecret,
			digits: 6,
			period: 30,
			algorithm: 'SHA1'
		}
	}

	return {
		success: true,
		secret: cleanedSecret,
		digits: 6,
		period: 30,
		algorithm: 'SHA1'
	}
}

export function generateTOTP(secret, digits, period, algorithm, timeOffset = 0) {
	const key = b32ToHex(secret)

	const epoch = Math.floor(Date.now() / 1000) + timeOffset
	const counter = Math.floor(epoch / period)

	const counterHex = counter.toString(16).padStart(16, '0')

	let hmacObj
	switch (algorithm) {
		case 'SHA256':
			hmacObj = CryptoJS.HmacSHA256(CryptoJS.enc.Hex.parse(counterHex), CryptoJS.enc.Hex.parse(key))
			break
		case 'SHA512':
			hmacObj = CryptoJS.HmacSHA512(CryptoJS.enc.Hex.parse(counterHex), CryptoJS.enc.Hex.parse(key))
			break
		default:
			hmacObj = CryptoJS.HmacSHA1(CryptoJS.enc.Hex.parse(counterHex), CryptoJS.enc.Hex.parse(key))
	}

	const hmac = hmacObj.toString(CryptoJS.enc.Hex)

	const offset = parseInt(hmac.substring(hmac.length - 1), 16)
	const truncatedHex = hmac.substr(offset * 2, 8)

	const truncatedDecimal = parseInt(truncatedHex, 16) & 0x7fffffff

	const otp = truncatedDecimal % Math.pow(10, digits)
	return otp.toString().padStart(digits, '0')
}

function b32ToHex(b32str) {
	const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
	let bits = ''
	let hex = ''

	b32str = b32str.replace(/=+$/, '')

	for (let i = 0; i < b32str.length; i++) {
		const val = charset.indexOf(b32str.charAt(i))
		if (val === -1) throw new Error('无效的字符')
		bits += val.toString(2).padStart(5, '0')
	}

	for (let i = 0; i + 4 <= bits.length; i += 4) {
		const chunk = bits.substr(i, 4)
		hex += parseInt(chunk, 2).toString(16)
	}

	return hex
}

export function formatCode(code) {
	if (code.length === 6) {
		return `${code.substring(0, 3)} ${code.substring(3)}`
	} else if (code.length === 8) {
		return `${code.substring(0, 4)} ${code.substring(4)}`
	}
	return code
}
